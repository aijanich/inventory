from django.contrib import admin
from django.utils.html import format_html
from .models import ClientProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "colored_balance")
    search_fields = ("user__username", "phone")

    def colored_balance(self, obj):
        if obj.balance > 0:
            color = "red"
        else:
            color = "green"

        return format_html(
            '<strong style="color:{};">{}</strong>',
            color,
            obj.balance,
        )

    colored_balance.short_description = "Balance"