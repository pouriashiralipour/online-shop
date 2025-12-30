from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

USER = get_user_model()


class Backend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        mobile = kwargs["mobile"]
        try:
            return USER.objects.get(mobile=mobile)
        except USER.DoesNotExist:
            return None
