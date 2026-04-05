from django.db import models
from django.conf import settings
from django.db.models import Sum


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.username

    @property
    def total_products(self):
        return self.transactions.aggregate(
            total=Sum("total_amount")
        )["total"] or 0

    @property
    def total_payments(self):
        return self.payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

    @property
    def balance(self):
        return self.total_products - self.total_payments
    