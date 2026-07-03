from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from app.acting import get_effective_user, is_effective_admin, redirect_admin_to_user_choice
from .forms import OrderForm
from .models import Order


def _orders_for_user(request):
    effective_user = get_effective_user(request)
    orders = Order.objects.select_related("user", "product", "color")
    if is_effective_admin(request):
        return orders
    return orders.filter(user=effective_user)


@login_required
def dashboard_orders(request):
    choice_redirect = redirect_admin_to_user_choice(request)
    if choice_redirect:
        return choice_redirect

    orders = _orders_for_user(request)
    paginator = Paginator(orders, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "orders/orders.html",
        {"orders": page_obj.object_list, "page_obj": page_obj},
    )


@login_required
def dashboard_order_create(request):
    choice_redirect = redirect_admin_to_user_choice(request)
    if choice_redirect:
        return choice_redirect

    effective_user = get_effective_user(request)
    if request.method == "POST":
        form = OrderForm(request.POST, request_user=effective_user)
        if form.is_valid():
            order = form.save(commit=False)
            if not is_effective_admin(request):
                order.user = effective_user
            order.save()
            return redirect("dashboard_orders")
    else:
        form = OrderForm(request_user=effective_user)

    return render(request, "orders/order_form.html", {"form": form, "mode": "create"})


@login_required
def dashboard_order_edit(request, pk):
    choice_redirect = redirect_admin_to_user_choice(request)
    if choice_redirect:
        return choice_redirect

    effective_user = get_effective_user(request)
    order = get_object_or_404(_orders_for_user(request), pk=pk)
    if not is_effective_admin(request) and order.user_id != effective_user.id:
        raise PermissionDenied()

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order, request_user=effective_user)
        if form.is_valid():
            updated = form.save(commit=False)
            if not is_effective_admin(request):
                updated.user = effective_user
            updated.save()
            return redirect("dashboard_orders")
    else:
        form = OrderForm(instance=order, request_user=effective_user)

    return render(
        request,
        "orders/order_form.html",
        {"form": form, "mode": "edit", "order": order},
    )
