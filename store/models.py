import uuid

from ckeditor.fields import RichTextField
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


def generate_unique_slug(instance, slug_field, title_field):
    """Generate a unique slug for the instance."""
    slug = slugify(getattr(instance, title_field), allow_unicode=True)
    Klass = instance.__class__
    qs = Klass.objects.filter(**{slug_field: slug}).exclude(id=instance.id)
    if qs.exists():
        from uuid import uuid4

        slug = f"{slug}-{uuid4().hex[:6]}"
        setattr(instance, slug_field, slug)
        return generate_unique_slug(instance, slug_field, title_field)
    setattr(instance, slug_field, slug)
    return instance


class Brand(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Brand Name"))
    english_title = models.CharField(_("English Brand Name"), max_length=50)
    cover = models.ImageField(_("cover"), upload_to="media/brands/")
    slug = models.SlugField(
        max_length=150,
        unique=True,
        allow_unicode=True,
        blank=True,
        null=True,
        verbose_name=_("Slug"),
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")
        ordering = ["title"]

    def __str__(self):
        return self.english_title

    def get_absolute_url(self):
        return reverse("store:brand-list", kwargs={"slug": self.slug})


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Category Name"))
    slug = models.SlugField(
        unique=True,
        allow_unicode=True,
        blank=True,
        null=True,
        verbose_name=_("Slug"),
    )
    parent = models.ForeignKey(
        "self",
        default=None,
        null=True,
        blank=True,
        verbose_name=_("Parent"),
        on_delete=models.SET_NULL,
        related_name="children",
    )
    cover = models.ImageField(
        _("Cover"),
        upload_to="media/categories/",
        blank=True,
        null=True,
    )
    is_parent = models.BooleanField(_("Is parent"))
    show_in_search_default = models.BooleanField(
        default=False,
        verbose_name=_("Show in default search list"),
        help_text=_(
            "If true, this category will be shown in the fixed search suggestions list."
        ),
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["datetime_created"]

    def __str__(self):
        return self.title

    def cover_img(self):
        try:
            return format_html("<img width=60 src='{}'>".format(self.cover.url))
        except:
            return ""

    cover_img.short_description = _("image")

    def get_absolute_url(self):
        return reverse("store:category-list", kwargs={"slug": self.slug})


class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Color Name"))
    hex_code = models.CharField(max_length=7, blank=True, verbose_name=_("Hex Code"))
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):

    title = models.CharField(max_length=200, verbose_name=_("Product Name"))
    english_title = models.CharField(
        blank=True, null=True, max_length=200, verbose_name=_("Product English Name")
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        allow_unicode=True,
        blank=True,
        null=True,
        verbose_name=_("Slug"),
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Brand"),
    )
    categories = models.ManyToManyField(
        Category, related_name="products", verbose_name=_("Categories")
    )
    tags = TaggableManager(blank=True, verbose_name=_("tags"))
    colors = models.ManyToManyField(
        Color,
        verbose_name=_("colors"),
        blank=True,
    )
    short_description = RichTextField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(_("image"), upload_to="products/")
    price = models.BigIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name=_("Price"),
    )
    discount_price = models.BigIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name=_("Discount Price"),
        blank=True,
        null=True,
    )
    stock = models.PositiveIntegerField(verbose_name=_("Stock"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    top_product = models.BooleanField(default=False, verbose_name=_("Top product"))
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["-datetime_created"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError(
                _("Discount price must be less than the original price.")
            )

    def get_discount_percentage(self):
        """Return the discount percentage if there is a discount."""
        if self.discount_price and self.discount_price < self.price:
            discount = 100 - (self.discount_price / self.price) * 100
            return round(discount)
        return None

    def get_absolute_url(self):
        return reverse("store:product-detail", kwargs={"slug": self.slug})


class ProductImages(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product"),
    )
    image = models.ImageField(upload_to="products/%Y/%m/%d/", verbose_name=_("Image"))
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ["datetime_created"]

    def __str__(self):
        return f"Image for {self.product.title}"


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="attributes",
        verbose_name=_("Product"),
    )
    key = models.CharField(max_length=200, verbose_name=_("Attribute Key"))
    value = models.CharField(max_length=200, verbose_name=_("Attribute Value"))
    price_modifier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Price Modifier"),
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")
        ordering = ["datetime_created"]

    def __str__(self):
        return f"{self.product.title} - {self.key}: {self.value}"


class Comment(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Product"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_comments",
        verbose_name=_("User"),
    )
    title = models.CharField(max_length=200, verbose_name=_("Comment Title"))
    text = models.TextField(verbose_name=_("Comment Text"))
    advantages = models.JSONField(blank=True, verbose_name=_("Advantages"))
    disadvantages = models.JSONField(blank=True, verbose_name=_("Disadvantages"))
    build_quality = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Build Quality"),
    )
    value_for_price = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Value for Price"),
    )
    innovation = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Innovation"),
    )
    features = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Features"),
    )
    ease_of_use = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Ease of Use"),
    )
    design = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Design"),
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_comments", blank=True
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="disliked_comments", blank=True
    )
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved"))
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.product.title}"


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer",
        verbose_name="user",
    )
    mobile = models.CharField(_("mobile"), max_length=11, unique=True)
    first_name = models.CharField(
        max_length=200, verbose_name=_("First Name"), blank=True, null=True
    )
    last_name = models.CharField(
        max_length=200, verbose_name=_("Last Name"), blank=True, null=True
    )
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    birth_date = models.DateField(null=True, blank=True)
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ["first_name"]

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Address(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("Customer"),
    )
    recipient_name = models.CharField(_("recipient_name"), max_length=50)
    recipient_last_name = models.CharField(_("recipient_last_name"), max_length=50)
    mobile = models.CharField(_("mobile"), max_length=11)
    province = models.CharField(max_length=100, verbose_name=_("Province"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    full_address = models.TextField(_("full_address"))
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal Code"))
    is_default = models.BooleanField(default=False, verbose_name=_("Is Default"))
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        ordering = ["-is_default", "city"]

    def __str__(self):
        return f"{self.customer.full_name} - {self.city}, {self.province}"


class Cart(models.Model):
    id = models.UUIDField(_("id"), default=uuid.uuid4, primary_key=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="carts",
        verbose_name=_("Customer"),
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Cart of {self.customer.full_name} - {self.num_of_items} items"

    @property
    def total_price(self):
        cart_items = self.items.all()
        total = sum([item.total_item_price for item in cart_items])
        return total

    @property
    def total_old_price(self):
        cart_items = self.items.all()
        total = sum([item.total_item_old_price for item in cart_items])
        return total

    @property
    def total_discount_price(self):
        cart_items = self.items.all()
        total = sum([item.total_discount_price for item in cart_items])
        return total

    @property
    def num_of_items(self):
        cart_items = self.items.all()
        quantity = sum([item.quantity for item in cart_items])
        return quantity


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name=_("Cart")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
        related_name="item",
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name=_("Quantity"), default=1
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        ordering = ["-datetime_created"]

    @property
    def total_discount_price(self):
        if self.product.discount_price is not None:
            discount = self.product.price - self.product.discount_price
            return discount * self.quantity
        return 0

    @property
    def total_item_old_price(self):
        return self.product.price * self.quantity

    @property
    def total_item_price(self):
        price_to_use = (
            self.product.discount_price
            if self.product.discount_price is not None
            else self.product.price
        )
        return price_to_use * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", _("Pending")),
        ("processing", _("Processing")),
        ("shipped", _("Shipped")),
        ("delivered", _("Delivered")),
        ("canceled", _("Canceled")),
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("Customer"),
    )
    address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, verbose_name=_("Address")
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Total Price"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
    )
    payment_method = models.CharField(max_length=50, verbose_name=_("Payment Method"))
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Order {self.id} by {self.customer.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name=_("Order")
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Attribute"),
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name=_("Quantity")
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Price"),
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in Order {self.order.id}"


class Wishlist(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="wishlist",
        verbose_name=_("Customer"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")
        unique_together = ("customer", "product")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"{self.product.title} in {self.customer.full_name}'s Wishlist"


class FavoriteList(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="favorite_lists",
        verbose_name=_("Customer"),
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("Products"),
        on_delete=models.CASCADE,
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Favorite List")
        verbose_name_plural = _("Favorite Lists")
        ordering = ["datetime_created"]
        unique_together = ("customer", "product")

    def __str__(self):
        return f"{self.customer.full_name}"


class Question(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("Product"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("User"),
    )
    text = models.TextField(verbose_name=_("Question Text"))
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved"))
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ["-datetime_created"]


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("Question"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("User"),
    )
    text = models.TextField(verbose_name=_("Answer Text"))
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved"))
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_answers", blank=True
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="disliked_answers", blank=True
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
        ordering = ["-datetime_created"]


# pages model
class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ("suggestion", _("Suggestion")),
        ("complaint", _("Complaint or Feedback")),
        ("order_tracking", _("Order Tracking")),
        ("after_sales", _("After-Sales Service")),
        ("warranty_inquiry", _("Warranty Inquiry")),
        ("management", _("Management")),
        ("accounting", _("Accounting and Financial Matters")),
        ("other", _("Other Topics")),
    ]

    subject = models.CharField(
        max_length=50, choices=SUBJECT_CHOICES, verbose_name=_("Subject")
    )
    full_name = models.CharField(max_length=100, verbose_name=_("Full Name"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=11, verbose_name=_("Phone Number"))
    message = models.TextField(verbose_name=_("Message"))
    attachment = models.FileField(
        upload_to="contact_attachments/",
        null=True,
        blank=True,
        verbose_name=_("Attachment"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")

    def __str__(self):
        return f"{self.full_name} - {self.get_subject_display()}"


class CategoryOfQuestion(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("title"))
    image = models.ImageField(upload_to="questions/", verbose_name=_("image"))
    slug = models.SlugField(
        max_length=255, verbose_name=_("slug"), unique=True, allow_unicode=True
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("datetime_created")
    )

    class Meta:
        verbose_name = _("CategoryOfQuestion")
        verbose_name_plural = _("CategoryOfQuestions")
        ordering = ["datetime_created"]

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("store:faq_category_view", args=[self.slug])


class QuestionsOfSites(models.Model):
    question = models.TextField(verbose_name=_("question"))
    answer = models.TextField(verbose_name=_("answer"))
    long_answer = models.TextField(verbose_name=_("long answer"), blank=True, null=True)
    slug = models.SlugField(
        max_length=255, verbose_name=_("slug"), unique=True, allow_unicode=True
    )
    category = models.ForeignKey(
        CategoryOfQuestion,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("category"),
    )
    repeat = models.BooleanField(default=False, verbose_name=_("repeat"))
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("datetime_created")
    )

    class Meta:
        verbose_name = _("Question of site")
        verbose_name_plural = _("Questions of site")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"{self.category}"

    def get_absolute_url(self):
        return reverse("store:faq_question_view", args=[self.slug])


class SearchLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_logs",
        verbose_name=_("User"),
    )
    query = models.CharField(max_length=255, verbose_name=_("Search Query"))
    category = models.ForeignKey(
        Category,
        related_name="search_logs",
        verbose_name=_("Category"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Search Log")
        verbose_name_plural = _("Search Logs")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"{self.query} ({self.category})"


def slug_pre_save(sender, instance, *args, **kwargs):
    if instance.slug is None:
        if hasattr(instance, "title"):
            generate_unique_slug(instance, "slug", "title")
        elif hasattr(instance, "english_title"):
            generate_unique_slug(instance, "slug", "english_title")


for model in [Brand, Category, Product]:
    pre_save.connect(slug_pre_save, sender=model)
