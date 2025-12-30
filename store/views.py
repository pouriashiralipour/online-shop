import json
from datetime import datetime
from statistics import mean

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import (
    Avg,
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    Max,
    Min,
    Prefetch,
    Q,
)
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST
from taggit.models import Tag

from users.models import UserHistory

from .cart import Cart as SessionCart
from .forms import AnswerForm, CommentForm, ContactUsForm, QuestionForm
from .models import (
    Answer,
    Brand,
    Cart,
    CartItem,
    Category,
    CategoryOfQuestion,
    Color,
    Comment,
    Customer,
    FavoriteList,
    Product,
    Question,
    QuestionsOfSites,
    SearchLog,
    Wishlist,
)

User = get_user_model()


# pages
def contact_us_view(request):
    if request.method == "POST":
        form = ContactUsForm(request.POST, request.FILES)
        if form.is_valid():
            contact = form.save(commit=False)
            if request.user.is_authenticated:
                contact.full_name = request.user.customer.full_name()
                contact.email = request.user.email
                contact.phone = request.user.customer.mobile
            contact.save()
            return JsonResponse(
                {"success": True, "message": "پیام شما با موفقیت ارسال شد."}
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    form = ContactUsForm()
    return render(request, "store/pages/contact-us.html", {"form": form})


def home_page_view(request):
    """
    Render the homepage with a list of active products.
    Cached categories and colors are loaded via Redis.
    """
    # Cache categories if not already cached
    products = cache.get("homepage_products")
    if products is None:
        products = (
            Product.objects.filter(is_active=True)
            .prefetch_related("colors", "comments")
            .annotate(
                approved_comment_count=Count(
                    "comments", filter=Q(comments__is_approved=True)
                ),
                avg_total_rating=Avg(
                    ExpressionWrapper(
                        (
                            F("comments__build_quality")
                            + F("comments__value_for_price")
                            + F("comments__innovation")
                            + F("comments__features")
                            + F("comments__ease_of_use")
                            + F("comments__design")
                        )
                        / 6.0,
                        output_field=FloatField(),
                    ),
                    filter=Q(comments__is_approved=True),
                ),
            )
        )
        cache.set("homepage_products", products, timeout=3600)

    context = {"products": products}
    return render(request, "store/home_page.html", context)


@require_GET
def search_results_view(request):
    query = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(
            Q(title__icontains=query)
            | Q(english_title__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()
    else:
        products = products.none()

    if query and products.exists():
        first_product = products.first()
        category = first_product.categories.first() if first_product else None
        SearchLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query=query,
            category=category,
        )

    top_search_categories = (
        Category.objects.filter(search_logs__isnull=False)
        .annotate(search_count=Count("search_logs"))
        .order_by("-search_count")[:5]
    )

    default_search_categories = Category.objects.filter(show_in_search_default=True)[:5]

    context = {
        "query": query,
        "products": products,
        "top_search_categories": top_search_categories,
        "default_search_categories": default_search_categories,
    }

    return render(request, "store/search_results.html", context)


@require_GET
def search_suggestions_view(request):
    query = request.GET.get("q", "").strip()

    suggestions = []
    if len(query) >= 4:
        products_qs = (
            Product.objects.filter(is_active=True)
            .filter(
                Q(title__icontains=query)
                | Q(english_title__icontains=query)
                | Q(tags__name__icontains=query)
            )
            .distinct()[:10]
        )
        suggestions = [
            {
                "title": product.title,
                "url": product.get_absolute_url(),
                "image": product.image.url if product.image else "",
            }
            for product in products_qs
        ]

    top_categories_qs = (
        Category.objects.filter(search_logs__isnull=False)
        .annotate(search_count=Count("search_logs"))
        .order_by("-search_count")[:5]
    )

    top_categories = [
        {
            "title": category.title,
            "url": reverse("store:category-list", kwargs={"slug": category.slug}),
        }
        for category in top_categories_qs
    ]

    default_categories_qs = Category.objects.filter(show_in_search_default=True)[:5]

    default_categories = [
        {
            "title": category.title,
            "url": reverse("store:category-list", kwargs={"slug": category.slug}),
        }
        for category in default_categories_qs
    ]

    return JsonResponse(
        {
            "products": suggestions,
            "top_categories": top_categories,
            "default_categories": default_categories,
        }
    )


def faq_view(request):
    category_of_questions = CategoryOfQuestion.objects.prefetch_related("questions")
    questions = QuestionsOfSites.objects.select_related("category")[:3]
    context = {
        "category_of_questions": category_of_questions,
        "questions": questions,
    }
    return render(request, "store/pages/faq.html", context)


def faq_category_view(request, slug):
    category_of_question = get_object_or_404(
        CategoryOfQuestion.objects.prefetch_related("questions"), slug=slug
    )
    context = {"category_of_question": category_of_question}
    return render(request, "store/pages/faq_category.html", context)


def faq_question_view(request, slug):
    question = get_object_or_404(
        QuestionsOfSites.objects.select_related("category"), slug=slug
    )
    questions = QuestionsOfSites.objects.filter(repeat=True)
    context = {"question": question, "questions": questions}
    return render(request, "store/pages/faq_question.html", context)


@require_GET
def product_quick_view(request, pk):
    """
    Return product data for a quick view modal as JSON.
    Includes colors, images, tags, attributes, ratings, and Q&A count.
    """
    try:
        product = Product.objects.prefetch_related(
            "colors",
            "images",
            "attributes",
            "tags",
            Prefetch(
                "questions",
                queryset=Question.objects.filter(is_approved=True).prefetch_related(
                    Prefetch(
                        "answers",
                        queryset=Answer.objects.filter(is_approved=True).only("id"),
                    )
                ),
            ),
            Prefetch("comments", queryset=Comment.objects.filter(is_approved=True)),
        ).get(pk=pk)

        # Use fallback image if gallery is empty
        gallery = [img.image.url for img in product.images.all()]
        if not gallery:
            gallery = [product.image.url]

        # Count approved questions and answers
        questions = product.questions.all()
        questions_count = len(questions)
        answers_count = sum(len(q.answers.all()) for q in questions)
        questions_and_answers_count = questions_count + answers_count

        # Count approved comments and calculate average rating
        comments = product.comments.filter(is_approved=True)
        total_comments = len(comments)

        if total_comments:
            total_rating = sum(
                (
                    comment.build_quality
                    + comment.value_for_price
                    + comment.innovation
                    + comment.features
                    + comment.ease_of_use
                    + comment.design
                )
                / 6.0
                for comment in comments
            )
            average_rating = round(total_rating / total_comments, 1)
        else:
            total_comments = 0
            average_rating = 0.0

        # Prepare data for JSON response
        data = {
            "id": product.id,
            "title": product.title,
            "english_title": product.english_title,
            "slug": product.slug,
            "image": product.image.url,
            "gallery": gallery,
            "tags": [
                {"name": tag.name, "slug": tag.slug} for tag in product.tags.all()
            ],
            "colors": [
                {"name": color.name, "hex": color.hex_code}
                for color in product.colors.all()
            ],
            "attributes": [
                {"key": attr.key, "value": attr.value}
                for attr in product.attributes.all()
            ],
            "comments_count": total_comments,
            "questions_and_answers_count": questions_and_answers_count,
            "average_rating": average_rating,
        }
        return JsonResponse({"success": True, "product": data})

    except Product.DoesNotExist:
        return JsonResponse({"success": False, "message": "محصول یافت نشد"}, status=404)


def product_category_listview(request, slug):
    """
    Show products in the selected category along with:
    - Prefetched colors
    - Annotated average rating and approved comment count
    - Children categories
    """

    color_prefetch = Prefetch("colors", queryset=Color.objects.all())

    base_qs = (
        Product.objects.filter(is_active=True)
        .prefetch_related(color_prefetch)
        .annotate(
            approved_comment_count=Count(
                "comments", filter=Q(comments__is_approved=True)
            ),
            avg_total_rating=Avg(
                ExpressionWrapper(
                    (
                        F("comments__build_quality")
                        + F("comments__value_for_price")
                        + F("comments__innovation")
                        + F("comments__features")
                        + F("comments__ease_of_use")
                        + F("comments__design")
                    )
                    / 6.0,
                    output_field=FloatField(),
                ),
                filter=Q(comments__is_approved=True),
            ),
        )
    )

    category = get_object_or_404(
        Category.objects.prefetch_related(
            Prefetch("products", queryset=base_qs),
        ),
        slug=slug,
    )

    products = category.products.all()

    brands = Brand.objects.filter(products__in=products).distinct()
    colors = Color.objects.filter(product__in=products).distinct()

    brand_ids = request.GET.getlist("brand")
    color_ids = request.GET.getlist("color")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    sort = request.GET.get("sort", "most_visited")

    try:
        selected_brand_ids = [int(b) for b in brand_ids]
    except (TypeError, ValueError):
        selected_brand_ids = []

    try:
        selected_color_ids = [int(c) for c in color_ids]
    except (TypeError, ValueError):
        selected_color_ids = []

    if selected_brand_ids:
        products = products.filter(brand_id__in=selected_brand_ids)

    if selected_color_ids:
        products = products.filter(colors__id__in=selected_color_ids).distinct()

    price_filters = {}
    if min_price and min_price.isdigit():
        price_filters["price__gte"] = int(min_price)
    if max_price and max_price.isdigit():
        price_filters["price__lte"] = int(max_price)

    if price_filters:
        products = products.filter(**price_filters)

    sort_map = {
        "most_visited": "-id",
        "best_selling": "-id",
        "most_popular": "-avg_total_rating",
        "newest": "-datetime_created",
        "cheapest": "-price",
        "most_expensive": "price",
    }

    order_by_field = sort_map.get(sort, "-id")
    products = products.order_by(order_by_field)

    selected_brand_ids = (
        [int(b) for b in selected_brand_ids] if selected_brand_ids else []
    )
    selected_color_ids = (
        [int(c) for c in selected_color_ids] if selected_color_ids else []
    )

    breadcrumb = get_category_breadcrumb(category)

    return render(
        request,
        "store/category-list.html",
        {
            "categories": category,
            "products": products,
            "brands": brands,
            "colors": colors,
            "breadcrumb": breadcrumb,
            "selected_brand_ids": selected_brand_ids,
            "selected_color_ids": selected_color_ids,
            "min_price": min_price,
            "max_price": max_price,
            "current_sort": sort,
        },
    )


def product_brand_listview(request, slug):

    products_qs = (
        Product.objects.filter(is_active=True)
        .annotate(
            approved_comment_count=Count(
                "comments", filter=Q(comments__is_approved=True)
            ),
            avg_total_rating=Avg(
                ExpressionWrapper(
                    (
                        F("comments__build_quality")
                        + F("comments__value_for_price")
                        + F("comments__innovation")
                        + F("comments__features")
                        + F("comments__ease_of_use")
                        + F("comments__design")
                    )
                    / 6.0,
                    output_field=FloatField(),
                ),
                filter=Q(comments__is_approved=True),
            ),
        )
        .prefetch_related("colors")
    )

    brand = get_object_or_404(
        Brand.objects.prefetch_related(
            Prefetch("products", queryset=products_qs),
        ),
        slug=slug,
    )

    # tab = request.GET.get("tab", "most_visited")

    # order_by = {
    #     "most_visited": "-id",
    #     "best_selling": "-id",
    #     "most_popular": "-id",
    #     "newest": "-datetime_created",
    #     "cheapest": "price",
    #     "most_expensive": "-price",
    # }.get(tab, "-id")

    products = brand.products.all()

    return render(
        request,
        "store/brand-list.html",
        {
            "brand": brand,
            "products": products,
        },
    )


def get_category_breadcrumb(category):
    breadcrumb = []
    while category is not None:
        breadcrumb.append(category)
        category = category.parent
    return breadcrumb[::-1]


def product_details_view(request, slug):
    """
    Render the product detail page with full product information,
    including images, attributes, tags, categories, comments, and Q&A.
    Also includes related products by tag and category.
    """

    # Fetch full product with all related data
    product = get_object_or_404(
        Product.objects.select_related("brand").prefetch_related(
            "images",
            "attributes",
            "colors",
            "tags",
            "categories",
            "categories__parent",
            Prefetch(
                "comments",
                queryset=Comment.objects.filter(is_approved=True)
                .annotate(num_likes=Count("likes"), num_dislikes=Count("dislikes"))
                .prefetch_related("likes", "dislikes"),
            ),
            Prefetch(
                "questions",
                queryset=Question.objects.filter(is_approved=True).prefetch_related(
                    Prefetch(
                        "answers",
                        queryset=Answer.objects.filter(is_approved=True)
                        .annotate(
                            num_likes=Count("likes"), num_dislikes=Count("dislikes")
                        )
                        .select_related("user__customer")
                        .prefetch_related("likes", "dislikes"),
                    )
                ),
            ),
        ),
        slug=slug,
    )

    # Record visit history for authenticated users
    if request.user.is_authenticated:
        customer = getattr(request, "customer", None)
        UserHistory.objects.update_or_create(
            customer=customer,
            product=product,
            defaults={"datetime_visited": datetime.now()},
        )

    # Extract related objects for template rendering
    colors = list(product.colors.all())
    comments = list(product.comments.all())
    categories = list(product.categories.all())
    questions = list(product.questions.all())

    # Count Q&A
    questions_count = len(questions)
    answers_count = sum(len(q.answers.all()) for q in questions)
    questions_and_answers_count = questions_count + answers_count

    # Calculate average scores
    def avg(attr):
        scores = [getattr(c, attr) for c in comments if getattr(c, attr) is not None]
        return round(mean(scores), 1) if scores else 0.0

    averages = {
        "avg_quality": avg("build_quality"),
        "avg_value": avg("value_for_price"),
        "avg_innovation": avg("innovation"),
        "avg_features": avg("features"),
        "avg_ease_of_use": avg("ease_of_use"),
        "avg_design": avg("design"),
        "total_avg": (
            round(
                mean(
                    [
                        (
                            c.build_quality
                            + c.value_for_price
                            + c.innovation
                            + c.features
                            + c.ease_of_use
                            + c.design
                        )
                        / 6.0
                        for c in comments
                        if all(
                            [
                                c.build_quality,
                                c.value_for_price,
                                c.innovation,
                                c.features,
                                c.ease_of_use,
                                c.design,
                            ]
                        )
                    ]
                ),
                1,
            )
            if comments
            else 0.0
        ),
    }

    # Fetch related products by categories and tags
    category_ids = product.categories.values_list("id", flat=True)
    tag_ids = product.tags.values_list("id", flat=True)

    related_by_categories = (
        Product.objects.filter(is_active=True)
        .exclude(id=product.id)
        .prefetch_related("colors")
        .filter(categories__id__in=category_ids)
        .distinct()
        .order_by("-datetime_created")
    )

    related_by_tags = list(
        Product.objects.filter(is_active=True)
        .exclude(id=product.id)
        .filter(tags__id__in=tag_ids)
        .distinct()
        .order_by("-datetime_created")
    )

    if len(related_by_tags) < 4:
        additional = related_by_categories.exclude(
            id__in=[p.id for p in related_by_tags]
        )[: 8 - len(related_by_tags)]
        related_by_tags += list(additional)

    # Attach product context for global context processor
    request.product = product
    request.product_comments = comments

    return render(
        request,
        "store/product-details.html",
        {
            "product": product,
            "averages": averages,
            "colors": colors,
            "comments": comments,
            "categories": categories,
            "questions": questions,
            "questions_and_answers_count": questions_and_answers_count,
            "related_products": related_by_tags,
        },
    )


def tag_list_view(request, slug=None):
    products_qs = (
        Product.objects.filter(is_active=True)
        .annotate(
            approved_comment_count=Count(
                "comments", filter=Q(comments__is_approved=True)
            ),
            avg_total_rating=Avg(
                ExpressionWrapper(
                    (
                        F("comments__build_quality")
                        + F("comments__value_for_price")
                        + F("comments__innovation")
                        + F("comments__features")
                        + F("comments__ease_of_use")
                        + F("comments__design")
                    )
                    / 6.0,
                    output_field=FloatField(),
                ),
                filter=Q(comments__is_approved=True),
            ),
        )
        .prefetch_related("colors")
    )

    tag = None

    if slug:
        tag = get_object_or_404(Tag, slug=slug)
        queryset = products_qs.filter(tags__in=[tag])

    products = queryset.order_by("-datetime_created")

    paginator = Paginator(products, 2)
    page = request.GET.get("page")

    try:
        paginated_products = paginator.page(page)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    return render(
        request,
        "store/tag-list.html",
        {
            "products": paginated_products,
            "tag": tag,
        },
    )


def top_products_view(request):
    products = (
        Product.objects.filter(is_active=True, top_product=True)
        .annotate(
            approved_comment_count=Count(
                "comments", filter=Q(comments__is_approved=True)
            ),
            avg_total_rating=Avg(
                ExpressionWrapper(
                    (
                        F("comments__build_quality")
                        + F("comments__value_for_price")
                        + F("comments__innovation")
                        + F("comments__features")
                        + F("comments__ease_of_use")
                        + F("comments__design")
                    )
                    / 6.0,
                    output_field=FloatField(),
                ),
                filter=Q(comments__is_approved=True),
            ),
        )
        .prefetch_related("colors")
    )

    return render(request, "store/top_products.html", {"products": products})


@login_required
def add_comment(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related(
            "images",
        ),
        slug=slug,
    )
    if request.method == "POST":
        form = CommentForm(request.POST)
        advantages = request.POST.get("advantages", "[]")
        disadvantages = request.POST.get("disadvantages", "[]")

        try:
            advantages = json.loads(advantages) if advantages else []
            disadvantages = json.loads(disadvantages) if disadvantages else []
        except json.JSONDecodeError:
            return JsonResponse({"bool": False, "error": "Invalid tag data."})

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = product
            comment.advantages = advantages
            comment.disadvantages = disadvantages
            comment.save()
            return redirect("store:product-detail", slug=product.slug)
    else:
        form = CommentForm()

    return render(
        request,
        "store/product-add-comment.html",
        {
            "form": form,
            "product": product,
        },
    )


@login_required
@require_POST
def like_dislike_comment(request, comment_id, action):
    comment = get_object_or_404(Comment, id=comment_id)

    has_liked = comment.likes.filter(id=request.user.id).exists()
    has_disliked = comment.dislikes.filter(id=request.user.id).exists()

    if action == "like" and not has_liked and not has_disliked:
        comment.likes.add(request.user)
    elif action == "dislike" and not has_liked and not has_disliked:
        comment.dislikes.add(request.user)
    else:
        return JsonResponse(
            {"success": False, "error": _("You have already submitted your review.")}
        )

    comment.save()
    return JsonResponse(
        {
            "success": True,
            "likes": comment.likes.count(),
            "dislikes": comment.dislikes.count(),
        }
    )


@login_required
@require_POST
def add_question(request, slug):
    product = get_object_or_404(Product, slug=slug)
    form = QuestionForm(request.POST)
    if form.is_valid():
        question = form.save(commit=False)
        question.user = request.user
        question.product = product
        question.save()
        return JsonResponse({"success": True})
    else:
        errors = form.errors.get("text", [_("An error occurred.")])[0]
        return JsonResponse({"success": False, "error": errors})


@login_required
@require_POST
def add_answer(request, slug, question_id):
    product = get_object_or_404(Product, slug=slug)
    question = get_object_or_404(Question, id=question_id, product=product)
    form = AnswerForm(request.POST)
    if form.is_valid():
        answer = form.save(commit=False)
        answer.user = request.user
        answer.question = question
        answer.save()
        return JsonResponse({"success": True})
    else:
        errors = form.errors.get("text", [_("An error occurred.")])[0]
        return JsonResponse({"success": False, "error": errors})


@login_required
@require_POST
def like_dislike_answer(request, answer_id, action):
    answer = get_object_or_404(Answer, id=answer_id)

    has_liked = answer.likes.filter(id=request.user.id).exists()
    has_disliked = answer.dislikes.filter(id=request.user.id).exists()

    if action == "like" and not has_liked and not has_disliked:
        answer.likes.add(request.user)
    elif action == "dislike" and not has_liked and not has_disliked:
        answer.dislikes.add(request.user)
    else:
        return JsonResponse(
            {"success": False, "error": _("You have already submitted your review.")}
        )

    answer.save()
    return JsonResponse(
        {
            "success": True,
            "likes": answer.likes.count(),
            "dislikes": answer.dislikes.count(),
        }
    )


def cart_view(request):
    """
    Display the shopping cart view.
    Loads wishlist data for authenticated users.
    """
    wishlist = None
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            customer = getattr(request, "customer", None)
        except Customer.DoesNotExist:
            customer = None
        if customer:
            wishlist = Wishlist.objects.select_related("customer").filter(
                customer=customer
            )
            wishlist_count = wishlist.count()

    return render(
        request,
        "store/cart.html",
        {
            "wishlist": wishlist,
            "wishlist_count": wishlist_count,
        },
    )


@require_POST
def add_to_cart(request):
    """
    Add a product to the user's cart.
    If user is authenticated, it uses the database cart.
    If not, it stores the item in a session-based guest cart.
    """
    product_id = int(request.POST.get("id"))
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        print("🔍 ADD TO CART DEBUG")
        print("User:", request.user)

        customer = getattr(request, "customer", None)

        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "حساب کاربری شما معتبر نیست."}
            )

        print("Customer:", customer)

        cart, created = Cart.objects.get_or_create(customer=customer)
        print("Cart ID:", cart.id)
        print("Product ID:", product.id)
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        wishlist = Wishlist.objects.filter(product=product, customer=customer)

        existing_items = cart.items.all()
        print(
            "Existing product IDs in cart:",
            [item.product.id for item in existing_items],
        )

        if cart_item:
            return JsonResponse(
                {"success": False, "message": _("Product Already in Cart")},
                status=200,
            )

        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        if wishlist:
            wishlist.delete()

        return JsonResponse(
            {
                "success": True,
                "message": _("Product Added Successfully."),
                "quantity": cart_item.quantity,
                "num_of_items": cart.num_of_items,
                "total_price": cart.total_price,
            },
            status=200,
        )

    else:
        cart = SessionCart(request)
        if product.stock <= 0:
            return JsonResponse(
                {"success": False, "message": "موجودی محصول کافی نیست."}
            )
        cart.add(product_id=product_id, quantity=1)
        return JsonResponse(
            {
                "success": True,
                "message": "محصول به سبد خرید مهمان اضافه شد.",
                "quantity": 1,
                "num_of_items": len(cart),
                "total_price": cart.get_total_price(),
            }
        )


@require_POST
def update_cart_item(request):
    product_id = int(request.POST.get("product_id"))
    quantity = int(request.POST.get("quantity"))
    product = get_object_or_404(Product, id=product_id)

    if quantity > product.stock:
        return JsonResponse(
            {
                "success": False,
                "message": _(
                    f"Insufficient stock. A maximum of {product.stock} items is available."
                ),
            },
            status=400,
        )

    if request.user.is_authenticated:
        customer = getattr(request, "customer", None)
        cart = get_object_or_404(Cart, customer=customer)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse(
            {
                "success": True,
                "quantity": cart_item.quantity,
                "message": _("The product quantity has been updated."),
                "num_of_items": cart.num_of_items,
                "total_price": cart.total_price,
            },
            status=200,
        )
    else:
        cart = SessionCart(request)
        cart.update(product_id=product_id, quantity=quantity)

        return JsonResponse(
            {
                "success": True,
                "message": "تعداد محصول به‌روزرسانی شد.",
                "quantity": quantity,
                "num_of_items": len(cart),
                "total_price": cart.get_total_price(),
            }
        )


@require_POST
def delete_cart_item(request):
    product_id = request.POST.get("product_id")

    if request.user.is_authenticated:
        customer = getattr(request, "customer", None)
        cart = get_object_or_404(Cart, customer=customer)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

        cart_item.delete()

        return JsonResponse(
            {
                "success": True,
                "message": _("The product has been removed from the cart."),
                "num_of_items": cart.num_of_items,
                "total_price": cart.total_price,
            },
            status=200,
        )
    else:
        cart = SessionCart(request)
        cart.remove(product_id)

        return JsonResponse(
            {
                "success": True,
                "message": "محصول از سبد خرید مهمان حذف شد.",
                "num_of_items": len(cart),
                "total_price": cart.get_total_price(),
            }
        )


@login_required
def add_to_wishlist(request):
    if request.method == "POST":
        product_id = int(request.POST.get("product_id"))
        if request.user.is_authenticated:
            customer = getattr(request, "customer", None)
            cart = Cart.objects.get(customer=customer)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            wishlist = Wishlist.objects.filter(customer=customer, product_id=product_id)
            if wishlist:
                return JsonResponse({"status": _("Product already in wishlist")})
            else:
                wishlist.create(customer=customer, product_id=product_id)
                cart_item.delete()
                return JsonResponse({"status": _("Product added to wishlist")})

        else:
            return JsonResponse({"status": "error", "message": _("Login To Continue")})
    return redirect("/")


@login_required
def delete_wishlist(request):
    if request.method == "POST":
        product_id = int(request.POST.get("product_id"))
        if request.user.is_authenticated:
            customer = getattr(request, "customer", None)
            wishlist = Wishlist.objects.filter(customer=customer, product_id=product_id)
            if wishlist:
                wishlist.delete()
                return JsonResponse({"status": _("Product removed from wishlist")})
            else:
                return JsonResponse({"status": _("Product not found in wishlist")})
        else:
            return JsonResponse({"status": "error", "message": _("Login To Continue")})
    return redirect("/")


@login_required
def add_to_favoritelist(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        if request.user.is_authenticated:
            customer = getattr(request, "customer", None)
            favorite_item = FavoriteList.objects.filter(
                customer=customer, product_id=product_id
            )
            if favorite_item:
                return JsonResponse({"status": _("Product already in favoritelist")})
            else:
                FavoriteList.objects.create(customer=customer, product_id=product_id)
                return JsonResponse({"status": _("Product added to favoritelist")})
        else:
            return JsonResponse({"status": "error", "message": _("Login To Continue")})
    else:
        return redirect("/")


@login_required
def delete_favoritelist(request):
    if request.method == "POST":
        product_id = int(request.POST.get("product_id"))
        if request.user.is_authenticated:
            customer = getattr(request, "customer", None)
            favoritelist = FavoriteList.objects.filter(
                customer=customer, product_id=product_id
            )
            if favoritelist:
                favoritelist.delete()
                return JsonResponse({"status": _("Product removed from favoritelist")})
            else:
                return JsonResponse({"status": _("Product not found in favoritelist")})
        else:
            return JsonResponse({"status": "error", "message": _("Login To Continue")})
    return redirect("/")


@login_required
def shipping(request):
    return render(request, "store/order/shipping.html")


@login_required
def payment(request):
    return render(request, "store/order/payment.html")


@login_required
def checkout(request):
    return render(request, "store/order/checkout.html")
