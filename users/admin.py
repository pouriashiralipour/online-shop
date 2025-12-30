from django.contrib import admin

from .models import User, UserHistory


@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ["full_name", "mobile", "datetime_created", "last_login"]


@admin.register(UserHistory)
class UserHistory(admin.ModelAdmin):
    list_display = [
        "customer",
        "product__title",
        "datetime_visited",
    ]
    list_filter = ["datetime_visited"]
