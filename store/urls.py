from django.urls import path, re_path

from . import views

app_name = "store"

urlpatterns = [
    # pages
    path("", views.home_page_view, name="home_page"),
    path("contact-us/", views.contact_us_view, name="contact_us"),
    path("faq/", views.faq_view, name="faq_view"),
    re_path(
        r"faq/categories/(?P<slug>[-\w]*)/$",
        views.faq_category_view,
        name="faq_category_view",
    ),
    re_path(
        r"faq/questions/(?P<slug>[-\w]*)/$",
        views.faq_question_view,
        name="faq_question_view",
    ),
    # products
    re_path(
        r"products/(?P<slug>[-\w]*)/$",
        views.product_details_view,
        name="product-detail",
    ),
    re_path(
        r"products/tags/(?P<slug>[-\w]+)/$",
        views.tag_list_view,
        name="tag-list",
    ),
    re_path(
        r"products/(?P<slug>[-\w]+)/add-comment/$",
        views.add_comment,
        name="add-comment",
    ),
    re_path(
        r"products/(?P<slug>[-\w]+)/add-question/$",
        views.add_question,
        name="add-question",
    ),
    re_path(
        r"products/(?P<slug>[-\w]+)/question/(?P<question_id>\d+)/add-answer/$",
        views.add_answer,
        name="add-answer",
    ),
    re_path(
        r"products/answer/(?P<answer_id>\d+)/(?P<action>like|dislike)/$",
        views.like_dislike_answer,
        name="like-dislike-answer",
    ),
    path(
        "products/comment/<int:comment_id>/<str:action>/",
        views.like_dislike_comment,
        name="like-dislike-comment",
    ),
    re_path(
        r"products/categories/(?P<slug>[-\w]+)/$",
        views.product_category_listview,
        name="category-list",
    ),
    re_path(
        r"products/brands/(?P<slug>[-\w]+)/$",
        views.product_brand_listview,
        name="brand-list",
    ),
    path("top_products/", views.top_products_view, name="top-products"),
    path("quick-view/<int:pk>/", views.product_quick_view, name="product-quick-view"),
    # carts
    path("cart/", views.cart_view, name="cart"),
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),
    path("update-cart-item/", views.update_cart_item, name="update-cart-item"),
    path("delete-cart-item/", views.delete_cart_item, name="delete-cart-item"),
    # wishlist
    path("add-to-wishlist/", views.add_to_wishlist, name="add-to-wishlist"),
    path("delete-wishlist/", views.delete_wishlist, name="delete-wishlist"),
    # favoritelist
    path("add-to-favorite/", views.add_to_favoritelist, name="add-to-favorite"),
    path("delete-favoritelist/", views.delete_favoritelist, name="delete-favoritelist"),
    # order
    path("shipping/", views.shipping, name="shipping"),
    path("payment/", views.payment, name="payment"),
    path("checkout/", views.checkout, name="checkout"),
    # search
    path("search/", views.search_results_view, name="product-search"),
    path(
        "search/suggestions/", views.search_suggestions_view, name="searchsuggestions"
    ),
]
