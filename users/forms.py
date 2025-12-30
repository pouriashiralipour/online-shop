import re

import jdatetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["mobile"]

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        if not mobile:
            raise ValidationError(_("Please Enter Phone Number ."))
        if not re.match(r"^\d{11}$", mobile):
            raise ValidationError(_("Phone Number must at least 11 digits ."))
        return mobile


class OTPForm(forms.Form):
    otp = forms.IntegerField(
        label="Enter OTP",
        widget=forms.NumberInput(attrs={"placeholder": _("OTP code")}),
    )
    error_messages = {
        "required": _("Please Enter OTP Code ."),
        "invalid": _("کد OTP باید یک عدد معتبر باشد."),
    }


class FullNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name:
            raise ValidationError(_("لطفاً نام را وارد کنید."))
        if len(first_name) > 15:
            raise ValidationError(_("نام نباید بیشتر از 15 حرف باشد."))
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name:
            raise ValidationError(_("لطفاً نام خانوادگی را وارد کنید."))
        if len(last_name) > 15:
            raise ValidationError(_("نام خانوادگی نباید بیشتر از 15 حرف باشد."))
        return last_name


class EmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError(_("لطفاً ایمیل را وارد کنید."))
        if len(email) > 254:
            raise ValidationError(_("ایمیل نباید بیشتر از 254 کاراکتر باشد."))
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            raise ValidationError(_("لطفاً یک ایمیل معتبر وارد کنید."))
        return email


class BirthDateForm(forms.Form):
    year = forms.IntegerField(
        label=_("سال"),
        required=True,
        error_messages={"required": _("لطفاً سال را وارد کنید.")},
    )
    month = forms.ChoiceField(
        label=_("ماه"),
        choices=[
            (1, "فروردین"),
            (2, "اردیبهشت"),
            (3, "خرداد"),
            (4, "تیر"),
            (5, "مرداد"),
            (6, "شهریور"),
            (7, "مهر"),
            (8, "آبان"),
            (9, "آ‌ذر"),
            (10, "دی"),
            (11, "بهمن"),
            (12, "اسفند"),
        ],
        required=True,
        error_messages={"required": _("لطفاً ماه را انتخاب کنید.")},
    )
    day = forms.IntegerField(
        label=_("روز"),
        required=True,
        error_messages={"required": _("لطفاً روز را وارد کنید.")},
    )

    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get("year")
        month = cleaned_data.get("month")
        day = cleaned_data.get("day")

        if year and month and day:
            try:
                year = int(year)
                month = int(month)
                day = int(day)

                if year < 1300 or year > 1403:
                    raise ValidationError(
                        {"year": _("سال باید بین 1300 تا 1403 باشد.")}
                    )
                if month < 1 or month > 12:
                    raise ValidationError({"month": _("ماه باید بین 1 تا 12 باشد.")})
                if day < 1 or day > 31:
                    raise ValidationError({"day": _("روز باید بین 1 تا 31 باشد.")})

                jdatetime.date(year, month, day)
            except ValueError:
                raise ValidationError(_("تاریخ وارد شده معتبر نیست."))
        return cleaned_data


class AvatarForm(forms.ModelForm):
    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if not avatar:
            raise ValidationError(_("لطفاً یک فایل انتخاب کنید."))
        if avatar.size > 2 * 1024 * 1024:
            raise ValidationError(_("حجم فایل نباید بیشتر از 2 مگابایت باشد."))
        if avatar.content_type not in ["image/jpeg", "image/png"]:
            raise ValidationError(_("فقط فایل‌های JPG و PNG مجاز هستند."))
        return avatar

    class Meta:
        model = User
        fields = ["avatar"]
