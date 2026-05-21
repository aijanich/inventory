from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ExpenseForm
from .models import Expense


def _require_admin(request):
    is_admin = request.user.is_staff or getattr(request.user, "role", "") == "admin"
    if not is_admin:
        raise PermissionDenied()


@login_required
def dashboard_expenses(request):
    _require_admin(request)

    qs = Expense.objects.select_related("created_by").all()
    total = qs.aggregate(total=Sum("amount"))["total"] or 0

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "expenses/expenses.html",
        {"expenses": page_obj.object_list, "page_obj": page_obj, "total": total},
    )


@login_required
def dashboard_expense_create(request):
    _require_admin(request)

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            return redirect("dashboard_expenses")
    else:
        form = ExpenseForm()

    return render(request, "expenses/expense_form.html", {"form": form, "mode": "create"})


@login_required
def dashboard_expense_edit(request, pk: int):
    _require_admin(request)

    obj = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("dashboard_expenses")
    else:
        form = ExpenseForm(instance=obj)

    return render(
        request,
        "expenses/expense_form.html",
        {"form": form, "mode": "edit", "expense": obj},
    )

