from django.db import models

class ProductTransaction(models.Model):
    client = models.ForeignKey(
        "clients.ClientProfile",
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE
    )

    color = models.ForeignKey(
        "colors.Color",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    date = models.DateField(auto_now=True)

    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        # Agar narx kiritilmagan bo‘lsa product narxini oladi
        if not self.price and self.product:
            self.price = self.product.price

        self.total_amount = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client} - {self.product}"


class Payment(models.Model):
    client = models.ForeignKey(
        "clients.ClientProfile",
        on_delete=models.CASCADE,
        related_name="payments"
    )
    date = models.DateField(auto_now=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.client} - {self.amount}"
