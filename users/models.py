from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from store.models import Customer, Product

from .user_manager import UserManager


class User(AbstractUser):
    username = None
    avatar = models.ImageField(
        _("avatar"), upload_to="media/users/avatars", blank=True, null=True
    )

    mobile = models.CharField(_("mobile"), max_length=11, unique=True)
    otp = models.PositiveIntegerField(_("otp"), blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    otp_datetime_created = models.DateTimeField(
        _("otp datetime created"), auto_now=True
    )
    datetime_created = models.DateTimeField(_("datetime created"), auto_now=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "mobile"

    objects = UserManager()

    backend = "users.backend.Backend"

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["datetime_created"]

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.mobile


class UserHistory(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name=_("customer"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="user_visits",
        verbose_name=_("Product"),
    )

    datetime_visited = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Visited At")
    )

    class Meta:
        verbose_name = _("User History")
        verbose_name_plural = _("User Histories")
        ordering = ["-datetime_visited"]
        unique_together = ("customer", "product")

    def __str__(self):
        return f"{self.customer.mobile} visited {self.product.title}"
