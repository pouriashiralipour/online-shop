from django.db.models.signals import post_save
from django.dispatch import receiver

from store.models import Customer

from .models import User


@receiver(post_save, sender=User)
def update_customer_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(
            user=instance,
            mobile=instance.mobile,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email,
            birth_date=instance.birth_date,
        )
    else:
        try:
            customer = instance.customer
            customer.mobile = instance.mobile
            customer.first_name = instance.first_name
            customer.last_name = instance.last_name
            customer.email = instance.email
            customer.birth_date = instance.birth_date
            customer.save()
        except Customer.DoesNotExist:
            Customer.objects.create(
                user=instance,
                mobile=instance.mobile,
                first_name=instance.first_name,
                last_name=instance.last_name,
                email=instance.email,
                birth_date=instance.birth_date,
            )
