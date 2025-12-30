from .models import Customer


class AttachCustomerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.customer = Customer.objects.filter(
                mobile=request.user.mobile
            ).first()
        return self.get_response(request)
