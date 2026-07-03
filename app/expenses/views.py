from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from app.acting import get_effective_user, is_effective_admin, redirect_admin_to_user_choice
from .forms import ExpenseForm
from .models import Expense


def _require_admin(request):
    choice_redirect = redirect_admin_to_user_choice(request)
    if choice_redirect:
        return choice_redirect
    if not is_effective_admin(request):
        raise PermissionDenied()
    return None


@login_required
def dashboard_expenses(request):
    redirect_response = _require_admin(request)
    if redirect_response:
        return redirect_response

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
    redirect_response = _require_admin(request)
    if redirect_response:
        return redirect_response

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = get_effective_user(request)
            obj.save()
            return redirect("dashboard_expenses")
    else:
        form = ExpenseForm()

    return render(request, "expenses/expense_form.html", {"form": form, "mode": "create"})


@login_required
def dashboard_expense_edit(request, pk: int):
    redirect_response = _require_admin(request)
    if redirect_response:
        return redirect_response

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
