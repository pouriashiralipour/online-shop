from collections import defaultdict

from django.core.cache import cache
from django.db.models import Count

from .cart import Cart as SessionCart
from .models import Cart, Category, FavoriteList


def build_category_tree(categories):
    tree = []
    lookup = defaultdict(list)

    for category in categories:
        lookup[category.parent_id].append(category)

    for category in categories:
        category.children_list = lookup.get(category.id, [])
        if category.parent_id is None:
            tree.append(category)

    return tree


def global_context(request):
    categories = cache.get("all_categories")
    if categories is None:
        all_categories = list(
            Category.objects.all().select_related("parent").order_by("datetime_created")
        )
        categories = build_category_tree(all_categories)
        cache.set("all_categories", categories, timeout=3600)

    cart_items = []
    product_ids_in_cart = []
    product_ids_in_favorite = []
    cart_item_quantity = 0
    favorite_item_count = 0
    total_price = total_old_price = total_discount_price = num_of_items = 0

    product = getattr(request, "product", None)

    if request.user.is_authenticated:
        customer = getattr(request, "customer", None)
        if customer:
            cart = (
                Cart.objects.select_related("customer")
                .prefetch_related("items__product__brand")
                .filter(customer=customer)
                .first()
            )
            if cart:
                items = cart.items.select_related("product", "product__brand")
                cart_items = [
                    {
                        "product": item.product,
                        "quantity": item.quantity,
                        "unit_price": item.product.discount_price or item.product.price,
                        "total_price": item.total_item_price,
                        "total_old_price": item.total_item_old_price,
                        "total_discount": item.total_discount_price,
                    }
                    for item in items
                ]
                total_price = cart.total_price
                total_old_price = cart.total_old_price
                total_discount_price = cart.total_discount_price
                num_of_items = cart.num_of_items
                product_ids_in_cart = [item.product_id for item in items]

                if product:
                    cart_item = next(
                        (
                            item
                            for item in cart_items
                            if item["product"].id == product.id
                        ),
                        None,
                    )
                    if cart_item:
                        cart_item_quantity = cart_item["quantity"]

            product_ids_in_favorite = list(
                FavoriteList.objects.filter(customer=customer).values_list(
                    "product_id", flat=True
                )
            )
            favorite_item_count = len(product_ids_in_favorite)

    else:
        cart = SessionCart(request)
        cart_items = list(cart)
        num_of_items = len(cart)
        total_price = cart.get_total_price()
        total_old_price = cart.get_total_old_price()
        total_discount_price = cart.get_total_discount()
        product_ids_in_cart = [
            item["product"].id for item in cart_items if "product" in item
        ]

        if product:
            cart_item = next(
                (item for item in cart_items if item["product"].id == product.id), None
            )
            if cart_item:
                cart_item_quantity = cart_item["quantity"]

    return {
        "global_categories": categories,
        "items": cart_items,
        "total_price": total_price,
        "total_old_price": total_old_price,
        "total_discount_price": total_discount_price,
        "num_of_items": num_of_items,
        "product_ids_in_cart": product_ids_in_cart,
        "cart_item_quantity": cart_item_quantity,
        "favorite_item_count": favorite_item_count,
        "product_ids_in_favorite": product_ids_in_favorite,
    }


def global_store_context(request):
    top_search_categories = (
        Category.objects.filter(search_logs__isnull=False)
        .annotate(search_count=Count("search_logs"))
        .order_by("-search_count")[:5]
    )

    default_search_categories = Category.objects.filter(show_in_search_default=True)[:5]

    return {
        "top_search_categories": top_search_categories,
        "default_search_categories": default_search_categories,
    }
