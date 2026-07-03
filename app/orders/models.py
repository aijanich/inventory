from django.conf import settings
from django.db import models


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    color = models.ForeignKey(
        "colors.Color",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    count = models.PositiveIntegerField()
    sizes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user} - {self.product} ({self.count})"
