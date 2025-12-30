from django.shortcuts import redirect
from django.urls import reverse


class EnsurePhoneVerifiedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            if request.path != reverse("users:verify"):
                return redirect("users:verify")

        if request.user.is_authenticated:
            if request.path == reverse("users:register"):
                return redirect("store:home_page")

        if request.user.is_authenticated:
            if request.path == reverse("users:verify"):
                return redirect("store:home_page")

        if request.user.is_authenticated:
            if request.path == reverse("users:welcome"):
                return redirect("store:home_page")

        if not request.user.is_authenticated:
            if request.path == reverse("users:welcome"):
                return redirect("store:home_page")

        return self.get_response(request)
