from django.db import models


class Product(models.Model):
    client = models.ForeignKey(
        "clients.ClientProfile",
        on_delete=models.CASCADE,
        related_name="products",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    comment = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"
