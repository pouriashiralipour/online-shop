from datetime import date

import jdatetime
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from store.models import Address, Comment, Customer, FavoriteList

from .forms import (
    AvatarForm,
    BirthDateForm,
    EmailForm,
    FullNameForm,
    OTPForm,
    RegisterForm,
)
from .models import User, UserHistory
from .services import (
    assign_otp,
    can_request_otp,
    get_client_ip,
    is_otp_valid,
    mark_otp_requested,
    verify_otp,
)


def register_view(request):
    form = RegisterForm()
    if request.method == "POST":
        mobile = request.POST.get("mobile")
        ip = get_client_ip(request)

        allowed, error = can_request_otp(mobile, ip)
        if not allowed:
            return JsonResponse({"error": error}, status=429)

        user, created = User.objects.get_or_create(mobile=mobile)
        assign_otp(user)
        mark_otp_requested(mobile, ip)
        request.session["mobile"] = user.mobile
        request.session["is_new_user"] = created
        return redirect("users:verify")

    return render(request, "users/login-register.html", {"form": form})

    form = RegisterForm()
    if request.method == "POST":
        mobile = request.POST.get("mobile")

        if not can_request_otp(mobile):
            return JsonResponse(
                {"error": "لطفاً کمی صبر کنید و دوباره تلاش کنید"}, status=429
            )

        user, created = User.objects.get_or_create(mobile=mobile)
        assign_otp(user)
        request.session["mobile"] = user.mobile
        request.session["is_new_user"] = created
        return redirect("users:verify")
    return render(request, "users/login-register.html", {"form": form})


def verify_view(request):
    mobile = request.session.get("mobile")
    is_new_user = request.session.get("is_new_user", False)

    if not mobile:
        return redirect("users:register")

    try:
        user = User.objects.get(mobile=mobile)
    except User.DoesNotExist:
        return redirect("users:register")

    form = OTPForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        otp = form.cleaned_data["otp"]

        if not is_otp_valid(user):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"error": _("The verification code has expired.")}, status=400
                )

        if not verify_otp(user, otp):
            error_message = "کد اشتباه است"
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"error": error_message}, status=400)
            form.add_error("otp", error_message)
            return render(
                request, "users/verification.html", {"form": form, "mobile": mobile}
            )

        user.is_active = True
        user.save()
        login(request, user)

        redirect_url = (
            reverse("users:welcome") if is_new_user else reverse("store:home_page")
        )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "redirect_url": redirect_url})

        return redirect(redirect_url)
    otp_created_at = user.otp_datetime_created
    time_elapsed = (now() - otp_created_at).total_seconds()

    return render(
        request,
        "users/verification.html",
        {
            "form": form,
            "mobile": mobile,
            "otp_time_elapsed": int(time_elapsed),
        },
    )


@require_POST
def resend_otp_view(request):
    mobile = request.session.get("mobile")
    if not mobile:
        return JsonResponse({"error": _("The mobile number is not valid.")}, status=400)

    ip = get_client_ip(request)
    allowed, error = can_request_otp(mobile, ip)
    if not allowed:
        return JsonResponse({"error": error}, status=429)

    try:
        user = User.objects.get(mobile=mobile)
        assign_otp(user)
        mark_otp_requested(mobile, ip)
        return JsonResponse(
            {"success": True, "message": _("A new code has been sent.")}
        )
    except User.DoesNotExist:
        return JsonResponse({"error": _("User not found.")}, status=404)

    mobile = request.session.get("mobile")
    if not mobile:
        return JsonResponse({"error": _("The mobile number is invalid.")}, status=400)

    if not can_request_otp(mobile):
        return JsonResponse(
            {"error": _("You cannot request a new one yet.")}, status=429
        )

    try:
        user = User.objects.get(mobile=mobile)
        assign_otp(user)
        return JsonResponse(
            {"success": True, "message": _("A new code has been sent.")}
        )
    except User.DoesNotExist:
        return JsonResponse({"error": _("User not found.")}, status=404)


def logout_view(request):
    logout(request)
    return redirect("store:home_page")


@login_required
def welcome_view(request):
    request.session.pop("is_new_user", False)
    return render(request, "users/welcome.html")


@login_required
def profile_view(request):
    customer = getattr(request, "customer", None)
    favorite_items = FavoriteList.objects.filter(customer=customer).select_related(
        "product"
    )
    history_items = UserHistory.objects.filter(customer=customer).select_related(
        "product"
    )
    context = {
        "favorite_items": favorite_items,
        "history_items": history_items,
    }

    return render(request, "users/dashboard.html", context)


@login_required
@require_POST
def add_address(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        return JsonResponse({"success": False, "error": "مشتری یافت نشد."}, status=400)

    data = request.POST
    recipient_name = data.get("recipient_name")
    recipient_last_name = data.get("recipient_last_name")
    province = data.get("province")
    city = data.get("city")
    mobile = data.get("mobile")
    postal_code = data.get("postal_code")
    full_address = data.get("full_address")
    is_default = data.get("is_default") == "on"

    # Validate inputs
    if not all(
        [
            recipient_name,
            recipient_last_name,
            province,
            city,
            mobile,
            postal_code,
            full_address,
        ]
    ):
        return JsonResponse(
            {"success": False, "error": "همه فیلدها الزامی هستند."}, status=400
        )
    # Validate mobile number
    mobile_validator = RegexValidator(
        regex=r"^09\d{9}$", message="شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود."
    )
    try:
        mobile_validator(mobile)
    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

    # Validate postal code
    postal_validator = RegexValidator(
        regex=r"^\d{10}$", message="کد پستی باید ۱۰ رقم و بدون خط تیره باشد."
    )
    try:
        postal_validator(postal_code)
    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

    # If setting as default, unset other default addresses
    if is_default:
        Address.objects.filter(customer=customer, is_default=True).update(
            is_default=False
        )
    # Create new address
    address = Address(
        customer=customer,
        recipient_name=recipient_name,
        recipient_last_name=recipient_last_name,
        province=province,
        city=city,
        mobile=mobile,
        postal_code=postal_code,
        full_address=full_address,
        is_default=is_default,
    )
    address.save()
    return JsonResponse({"success": True, "message": "آدرس با موفقیت ذخیره شد"})


@login_required
@require_POST
def edit_address(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        return JsonResponse({"success": False, "error": "مشتری یافت نشد."}, status=400)

    address_id = request.POST.get("address_id")
    address = get_object_or_404(Address, id=address_id, customer=customer)

    data = request.POST
    recipient_name = data.get("recipient_name")
    recipient_last_name = data.get("recipient_last_name")
    province = data.get("province")
    city = data.get("city")
    mobile = data.get("mobile")
    postal_code = data.get("postal_code")
    full_address = data.get("full_address")
    is_default = data.get("is_default") == "on"

    # Validate inputs
    if not all(
        [
            recipient_name,
            recipient_last_name,
            province,
            city,
            mobile,
            postal_code,
            full_address,
        ]
    ):
        return JsonResponse(
            {"success": False, "error": "همه فیلدها الزامی هستند."}, status=400
        )

    # Validate mobile number
    mobile_validator = RegexValidator(
        regex=r"^09\d{9}$", message="شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود."
    )
    try:
        mobile_validator(mobile)
    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

    # Validate postal code
    postal_validator = RegexValidator(
        regex=r"^\d{10}$", message="کد پستی باید ۱۰ رقم و بدون خط تیره باشد."
    )
    try:
        postal_validator(postal_code)
    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

    # If setting as default, unset other default addresses
    if is_default:
        Address.objects.filter(customer=customer, is_default=True).update(
            is_default=False
        )

    # Update address
    address.recipient_name = recipient_name
    address.recipient_last_name = recipient_last_name
    address.province = province
    address.city = city
    address.mobile = mobile
    address.postal_code = postal_code
    address.full_address = full_address
    address.is_default = is_default
    address.save()

    return JsonResponse({"success": True, "message": "آدرس با موفقیت بروز شد ."})


@login_required
@require_POST
def delete_address(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        return JsonResponse({"success": False, "error": "مشتری یافت نشد."}, status=400)

    address_id = request.POST.get("address_id")
    address = get_object_or_404(Address, id=address_id, customer=customer)
    address.delete()
    return JsonResponse({"success": True})


@login_required
def get_address(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        return JsonResponse({"success": False, "error": "مشتری یافت نشد."}, status=400)

    address_id = request.GET.get("address_id")
    address = get_object_or_404(Address, id=address_id, customer=customer)
    data = {
        "id": address.id,
        "recipient_name": address.recipient_name,
        "recipient_last_name": address.recipient_last_name,
        "province": address.province,
        "city": address.city,
        "mobile": address.mobile,
        "postal_code": address.postal_code,
        "full_address": address.full_address,
        "is_default": address.is_default,
    }
    return JsonResponse({"success": True, "address": data})


@login_required
def profile_addresse_view(request):
    return render(request, "users/profile-addresses.html")


@login_required
def profile_comments_view(request):
    comments = Comment.objects.filter(user=request.user).select_related("product")
    return render(request, "users/profile-comments.html", {"comments": comments})


@login_required
def profile_favorites_view(request):
    try:
        customer = getattr(request, "customer", None)
        favorite_items = FavoriteList.objects.filter(customer=customer).select_related(
            "product"
        )
        return render(
            request, "users/profile-favorites.html", {"favorite_item": favorite_items}
        )
    except customer.DoesNotExist:
        return render(request, "users/profile-favorites.html", {"favorite_item": []})


@login_required
def profile_giftcards_view(request):
    return render(request, "users/profile-giftcards.html")


@login_required
def profile_my_order_detail_view(request):
    return render(request, "users/profile-my-order-detail.html")


@login_required
def profile_my_orders_view(request):
    return render(request, "users/profile-my-orders.html")


@login_required
def profile_notification_view(request):
    return render(request, "users/profile-notification.html")


@login_required
def profile_personal_info_view(request):
    user = request.user
    birth_date_shamsi = None
    birth_date_shamsi_text = None
    birth_month = None

    months = {
        1: "فروردین",
        2: "اردیبهشت",
        3: "خرداد",
        4: "تیر",
        5: "مرداد",
        6: "شهریور",
        7: "مهر",
        8: "آبان",
        9: "آ‌ذر",
        10: "دی",
        11: "بهمن",
        12: "اسفند",
    }

    if user.birth_date:
        shamsi_date = jdatetime.date.fromgregorian(
            year=user.birth_date.year,
            month=user.birth_date.month,
            day=user.birth_date.day,
        )
        year = shamsi_date.year
        month = months[shamsi_date.month]
        day = shamsi_date.day
        birth_date_shamsi = f"{year}/{shamsi_date.month:02d}/{day:02d}"
        birth_date_shamsi_text = f"{day} {month} {year}"
        birth_month = shamsi_date.month

    months_list = [(i, month) for i, month in enumerate(months.values(), 1)]

    return render(
        request,
        "users/profile-personal-info.html",
        {
            "birth_date_shamsi": birth_date_shamsi,
            "birth_date_shamsi_text": birth_date_shamsi_text,
            "months": months_list,
            "birth_month": birth_month,
        },
    )


@login_required
def profile_tickets_add_view(request):
    return render(request, "users/profile-tickets-add.html")


@login_required
def profile_tickets_detail_view(request):
    return render(request, "users/profile-tickets-detail.html")


@login_required
def profile_tickets_view(request):
    return render(request, "users/profile-tickets.html")


@login_required
def profile_user_history_view(request):
    try:
        customer = getattr(request, "customer", None)
    except Customer.DoesNotExist:
        customer = None

    # Fetch user history with related product data
    history_items = (
        UserHistory.objects.filter(customer=customer)
        .select_related("product", "customer")
        .order_by("-datetime_visited")[:10]
    )
    context = {
        "history_items": history_items,
        "customer": customer,
    }

    return render(request, "users/profile-user-history.html", context)


@login_required
@require_POST
def delete_history_view(request):
    product_id = request.POST.get("product_id")
    customer = getattr(request, "customer", None)
    if not product_id:
        return JsonResponse(
            {"success": False, "error": "شناسه محصول نامعتبر است."}, status=400
        )

    try:
        history_item = UserHistory.objects.get(customer=customer, product_id=product_id)
        history_item.delete()
        return JsonResponse({"success": True, "message": "محصول از تاریخچه حذف شد."})
    except UserHistory.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "محصول در تاریخچه یافت نشد."}, status=404
        )


@login_required
def update_full_name(request):
    if request.method == "POST":
        form = FullNameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def update_email(request):
    if request.method == "POST":
        form = EmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def update_birth_date(request):
    if request.method == "POST":
        form = BirthDateForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data["year"]
            month = form.cleaned_data["month"]
            day = form.cleaned_data["day"]

            try:
                shamsi_date = jdatetime.date(int(year), int(month), int(day))
                gregorian_date = shamsi_date.togregorian()
                birth_date = date(
                    gregorian_date.year, gregorian_date.month, gregorian_date.day
                )

                request.user.birth_date = birth_date
                request.user.save()
                return JsonResponse({"success": True})
            except ValueError as e:
                return JsonResponse({"success": False, "errors": {"__all__": [str(e)]}})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def update_avatar(request):
    if request.method == "POST":
        form = AvatarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
@require_POST
def update_mobile(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data.get("mobile")
            ip = get_client_ip(request)

            allowed, error = can_request_otp(mobile, ip)
            if not allowed:
                return JsonResponse({"success": False, "error": error}, status=429)

            request.session["new_mobile"] = mobile
            request.session["mobile_change_user_id"] = request.user.id

            try:
                user = User.objects.get(id=request.user.id)
                assign_otp(user)
                mark_otp_requested(mobile, ip)
                return JsonResponse({"success": True, "next_step": "verify_otp"})
            except User.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": _("کاربر یافت نشد.")}, status=404
                )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return JsonResponse(
        {"success": False, "error": _("روش درخواست نامعتبر است.")}, status=400
    )


@login_required
@require_POST
def verify_mobile_otp(request):
    if request.method == "POST":
        form = OTPForm(request.POST)
        new_mobile = request.session.get("new_mobile")
        user_id = request.session.get("mobile_change_user_id")

        if not new_mobile or not user_id:
            return JsonResponse(
                {"success": False, "error": _("داده‌های سشن نامعتبر است.")}, status=400
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": _("کاربر یافت نشد.")}, status=404
            )

        if form.is_valid():
            otp = form.cleaned_data["otp"]

            if not is_otp_valid(user):
                return JsonResponse(
                    {"success": False, "error": _("کد تأیید منقضی شده است.")},
                    status=400,
                )

            if not verify_otp(user, otp):
                return JsonResponse(
                    {"success": False, "error": _("کد اشتباه است.")}, status=400
                )

            user.mobile = new_mobile
            user.save()

            request.session.pop("new_mobile", None)
            request.session.pop("mobile_change_user_id", None)

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return JsonResponse(
        {"success": False, "error": _("روش درخواست نامعتبر است.")}, status=400
    )
