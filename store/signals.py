from django.contrib.auth.signals import user_logged_in
from django.core.cache import cache
from django.dispatch import receiver

from .cart import Cart as SessionCart
from .models import Cart, CartItem, Customer


@receiver(user_logged_in)
def merge_session_cart_with_db(sender, user, request, **kwargs):
    """
    Signal handler that merges the session-based shopping cart with the
    authenticated user's database cart upon login.

    This ensures that any items added to the cart before logging in
    (as an anonymous user) are transferred to the user's persistent cart
    in the database.

    Steps performed:
    1. Retrieve or create a Customer object linked to the logged-in user.
    2. Retrieve or create a Cart object for the customer.
    3. Load items from the session-based cart.
    4. For each item in the session cart:
        - If the product already exists in the database cart, increment its quantity.
        - If not, create a new CartItem in the database cart.
        - Ensure that quantities do not exceed the available product stock.
    5. Clear the session cart and mark the session as modified.
    6. Invalidate related cache entries to reflect updated cart data.
    """

    session_cart = SessionCart(request)

    if not session_cart:
        return

    try:
        customer = user.customer
    except Customer.DoesNotExist:
        return

    db_cart, created = Cart.objects.get_or_create(customer=customer)

    for item in session_cart:
        product = item["product"]
        quantity = item["quantity"]

        cart_item, created = CartItem.objects.get_or_create(
            cart=db_cart, product=product
        )
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

    session_cart.clear()
