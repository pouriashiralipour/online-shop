from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from jalali_date.admin import ModelAdminJalaliMixin, TabularInlineJalaliMixin

from .models import (
    Address,
    Answer,
    Brand,
    Cart,
    CartItem,
    Category,
    CategoryOfQuestion,
    Color,
    Comment,
    ContactMessage,
    Customer,
    FavoriteList,
    Order,
    OrderItem,
    Product,
    ProductAttribute,
    ProductImages,
    Question,
    QuestionsOfSites,
    Wishlist,
)


@admin.register(QuestionsOfSites)
class QuestionOfSiteAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("question",)}


@admin.register(CategoryOfQuestion)
class CategoryOfQuestionAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    pass


@admin.register(Brand)
class BrandAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("title", "slug", "datetime_created")
    list_filter = ("datetime_created",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Category)
class CategoryAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("title", "cover_img", "is_parent", "datetime_created")
    list_filter = ("datetime_created",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Color)
class ColorAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("name", "hex_code", "datetime_created")
    list_filter = ("datetime_created",)
    search_fields = ("name",)


class ProductImagesInline(TabularInlineJalaliMixin, admin.TabularInline):
    model = ProductImages
    extra = 1
    fields = ("image", "datetime_created")
    readonly_fields = ("datetime_created",)


class ProductAttributeInline(TabularInlineJalaliMixin, admin.TabularInline):
    model = ProductAttribute
    extra = 1
    fields = ("key", "value", "datetime_created")
    readonly_fields = ("datetime_created",)


@admin.register(Product)
class ProductAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("title", "brand", "price", "stock", "is_active", "datetime_created")
    list_filter = ("is_active", "brand", "categories", "datetime_created")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImagesInline, ProductAttributeInline]
    filter_horizontal = ("categories",)


@admin.register(ProductImages)
class ProductImagesAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("product", "datetime_created")
    list_filter = ("datetime_created",)
    search_fields = ("product__title",)


@admin.register(ProductAttribute)
class ProductAttributeAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("product", "key", "value")
    list_filter = ("key", "datetime_created")
    search_fields = ("product__title", "key", "value")


@admin.register(Comment)
class CommentAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = (
        "product",
        "user__first_name",
        "user__last_name",
        "title",
        "is_approved",
        "datetime_created",
    )
    list_filter = ("is_approved", "datetime_created")
    search_fields = ("title", "text", "product__title", "user__username")
    actions = ["approve_comments"]
    readonly_fields = ("datetime_created", "datetime_updated")
    fieldsets = (
        (None, {"fields": ("product", "user", "title", "text", "is_approved")}),
        (
            _("Ratings"),
            {
                "fields": (
                    "build_quality",
                    "value_for_price",
                    "innovation",
                    "features",
                    "ease_of_use",
                    "design",
                )
            },
        ),
        (
            _("Advantages and Disadvantages"),
            {"fields": ("advantages", "disadvantages")},
        ),
        (
            _("Likes and Dislikes"),
            {"fields": ("likes", "dislikes")},
        ),
        (
            _("Timestamps"),
            {
                "fields": ("datetime_created", "datetime_updated"),
            },
        ),
    )

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    approve_comments.short_description = _("Approve selected comments")


@admin.register(Customer)
class CustomerAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("full_name", "mobile", "email", "birth_date", "datetime_created")
    search_fields = ("full_name", "email", "user__username")
    readonly_fields = ("datetime_created", "datetime_updated")


class AddressInline(TabularInlineJalaliMixin, admin.TabularInline):
    model = Address
    extra = 1
    fields = ("province", "city", "full_address", "postal_code", "is_default")
    readonly_fields = ("datetime_created",)


@admin.register(Address)
class AddressAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = (
        "customer",
        "city",
        "full_address",
        "is_default",
        "datetime_created",
    )
    list_filter = ("is_default", "datetime_created")
    search_fields = ("customer__full_name", "city", "full_address")


class CartItemInline(TabularInlineJalaliMixin, admin.TabularInline):
    model = CartItem
    extra = 1
    fields = ("product", "quantity", "datetime_created")
    readonly_fields = ("datetime_created",)


@admin.register(Cart)
class CartAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("customer", "datetime_created")
    search_fields = ("customer__full_name",)
    inlines = [CartItemInline]
    readonly_fields = ("datetime_created", "datetime_updated")


@admin.register(CartItem)
class CartItemAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = (
        "cart",
        "product",
        "quantity",
        "datetime_created",
    )
    list_filter = ("datetime_created",)
    search_fields = ("product__title", "cart__customer__full_name")


class OrderItemInline(TabularInlineJalaliMixin, admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ("product", "quantity", "price", "datetime_created")
    readonly_fields = ("datetime_created",)


@admin.register(Order)
class OrderAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("id", "customer", "total_price", "status", "datetime_created")
    list_filter = ("status", "datetime_created")
    search_fields = ("customer__full_name",)
    inlines = [OrderItemInline]
    readonly_fields = ("datetime_created", "datetime_updated")


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price", "datetime_created")
    list_filter = ("datetime_created",)
    search_fields = ("product__title", "order__customer__full_name")


@admin.register(Wishlist)
class WishlistAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("customer", "product", "datetime_created")
    list_filter = ("datetime_created",)
    search_fields = ("customer__full_name", "product__title")


@admin.register(FavoriteList)
class FavoriteListAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ("customer", "datetime_created")
    list_filter = ("datetime_created",)
    search_fields = ("customer__full_name",)


@admin.register(Question)
class QuestionAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "text",
        "is_approved",
        "datetime_created",
    )
    list_filter = ("is_approved", "datetime_created")
    search_fields = ("text", "product__title", "user__last_name")
    actions = ["approve_questions"]
    readonly_fields = ("datetime_created", "datetime_updated")
    fieldsets = (
        (None, {"fields": ("product", "user", "text", "is_approved")}),
        (
            _("Timestamps"),
            {
                "fields": ("datetime_created", "datetime_updated"),
            },
        ),
    )

    def approve_questions(self, request, queryset):
        queryset.update(is_approved=True)

    approve_questions.short_description = _("Approve selected questions")


@admin.register(Answer)
class AnswerAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = (
        "question__text",
        "user",
        "text",
        "is_approved",
        "datetime_created",
    )
    list_filter = ("is_approved", "datetime_created")
    search_fields = ("text", "question__text", "user__last_name)")
    actions = ["approve_answers"]
    readonly_fields = ("datetime_created", "datetime_updated")
    fieldsets = (
        (None, {"fields": ("question", "user", "text", "is_approved")}),
        (
            _("Likes and Dislikes"),
            {"fields": ("likes", "dislikes")},
        ),
        (
            _("Timestamps"),
            {
                "fields": ("datetime_created", "datetime_updated"),
            },
        ),
    )

    def approve_answers(self, request, queryset):
        queryset.update(is_approved=True)

    approve_answers.short_description = _("Approve selected answers")
