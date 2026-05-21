from django.contrib import admin

from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "amount", "created_by", "created_at")
    list_filter = ("date",)
    search_fields = ("description", "created_by__username")

