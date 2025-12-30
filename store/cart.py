from .models import Product


class Cart:
    """
    A session-based shopping cart for managing product items.

    This cart stores product data in the user's session and supports operations like
    add, update, remove, clear, and iteration over cart items. It also calculates
    totals including discounts.
    """

    def __init__(self, request):
        """
        Initialize the cart using the current Django request session.

        Args:
            request (HttpRequest): The current request object.
        """

        self.request = request
        self.session = request.session
        cart = self.session.get("cart")

        if not cart:
            cart = self.session["cart"] = {}

        self.cart = cart

    def add(self, product_id, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.

        Args:
            product_id (int or str): The ID of the product to add.
            quantity (int): Quantity of the product to add.
            override_quantity (bool): If True, set quantity absolutely; otherwise, increment.
        """

        product_id = str(product_id)

        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0}

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        self.save()

    def update(self, product_id, quantity):
        """
        Update the quantity of a product in the cart.

        Args:
            product_id (int or str): The ID of the product to update.
            quantity (int): New quantity to set.
        """

        product_id = str(product_id)

        if product_id in self.cart:
            self.cart[product_id]["quantity"] = quantity
            self.save()

    def remove(self, product_id):
        """
        Remove a product from the cart.

        Args:
            product_id (int or str): The ID of the product to remove.
        """

        product_id = str(product_id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """
        Remove all items from the cart.
        """

        self.session["cart"] = {}
        self.save()

    def save(self):
        """
        Mark the session as modified to make sure it's saved.
        """

        self.session.modified = True

    def __len__(self):
        """
        Return the total number of items in the cart.

        Returns:
            int: Total quantity of all items.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.

        Yields:
            dict: A dictionary containing:
                - product (Product): The product instance.
                - quantity (int): Quantity in cart.
                - unit_price : Price per unit (discount or regular).
                - total_price : unit_price × quantity.
                - total_old_price : product.price × quantity.
                - total_discount : Total discount for that item.
        """

        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(product.id): product for product in products}

        cart_copy = self.cart.copy()

        for product_id, item in cart_copy.items():
            product = product_map.get(product_id)
            if not product:
                self.remove(product_id)
                continue

            quantity = item["quantity"]
            unit_price = (
                product.discount_price if product.discount_price else product.price
            )

            yield {
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": unit_price * quantity,
                "total_old_price": product.price * quantity,
                "total_discount": (
                    (product.price - unit_price) * quantity
                    if product.discount_price
                    else 0
                ),
            }

    def get_total_price(self):
        """
        Get the total price of all items after discounts.

        Returns:
            int: Total discounted price.
        """

        return sum(item["total_price"] for item in self)

    def get_total_old_price(self):
        """
        Get the total price of all items without any discounts.

        Returns:
            int: Total original price.
        """

        return sum(item["total_old_price"] for item in self)

    def get_total_discount(self):
        """
        Get the total discount for all items.

        Returns:
            int: Total amount saved due to discounts.
        """

        return sum(item["total_discount"] for item in self)
