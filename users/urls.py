from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("verify/", views.verify_view, name="verify"),
    path("verify/resent/", views.resend_otp_view, name="resend_otp"),
    path("welcome/", views.welcome_view, name="welcome"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.profile_view, name="dashboard"),
    path(
        "dashboard/user-history", views.profile_user_history_view, name="user-history"
    ),
    path("dashboard/history/delete/", views.delete_history_view, name="delete-history"),
    path("dashboard/tickets", views.profile_tickets_view, name="tickets"),
    path("dashboard/add-ticket", views.profile_tickets_add_view, name="add-ticket"),
    path(
        "dashboard/ticket-details",
        views.profile_tickets_detail_view,
        name="ticket-details",
    ),
    path(
        "dashboard/personal-info",
        views.profile_personal_info_view,
        name="personal-info",
    ),
    path(
        "dashboard/notification", views.profile_notification_view, name="notifications"
    ),
    path("dashboard/my-orders", views.profile_my_orders_view, name="my-orders"),
    path(
        "dashboard/my-order-detail",
        views.profile_my_order_detail_view,
        name="my-order-detail",
    ),
    path("dashboard/giftcards", views.profile_giftcards_view, name="giftcards"),
    path("dashboard/favorites", views.profile_favorites_view, name="favorites"),
    path("dashboard/comments", views.profile_comments_view, name="comments"),
    path("dashboard/addresses", views.profile_addresse_view, name="address"),
    path("address/add/", views.add_address, name="add_address"),
    path("address/edit/", views.edit_address, name="edit_address"),
    path("address/delete/", views.delete_address, name="delete_address"),
    path("address/get/", views.get_address, name="get_address"),
    path("update-full-name/", views.update_full_name, name="update_full_name"),
    path("update-email/", views.update_email, name="update_email"),
    path("update-birth-date/", views.update_birth_date, name="update_birth_date"),
    path("update-avatar/", views.update_avatar, name="update_avatar"),
    path("update-mobile/", views.update_mobile, name="update_mobile"),
    path("verify-mobile-otp/", views.verify_mobile_otp, name="verify_mobile_otp"),
]
