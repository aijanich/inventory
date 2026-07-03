from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import ProductTransaction, Payment
from .forms import ProductTransactionForm, PaymentForm, ClientPaymentForm
from django.shortcuts import render, redirect, get_object_or_404
from app.acting import get_effective_user, is_effective_admin, redirect_admin_to_user_choice


@login_required
def create_transaction(request):

    choice_redirect = redirect_admin_to_user_choice(request)
    if choice_redirect:
        return choice_redirect

    if not is_effective_admin(request):
        raise PermissionDenied()

    client_id = request.GET.get("client") if request.method != "POST" else request.POST.get("client")
    if request.method == "POST":
        form = ProductTransactionForm(request.POST, client=client_id)

        if form.is_valid():
            form.save()
            return redirect("client_dashboard")

    else:
        form = ProductTransactionForm(initial={"client": client_id} if client_id else None, client=client_id)

    return render(request, "transactions/create_transaction.html", {"form": form})

@login_required
def create_payment(request):

    choice_redirect = redirect_admin_to_user_choice(request)
    if choice_redirect:
        return choice_redirect

    effective_user = get_effective_user(request)
    if effective_user.role != "client":
        raise PermissionDenied()

    if request.method == "POST":
        form = ClientPaymentForm(request.POST)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.client = effective_user.profile
            payment.save()

            return redirect("client_dashboard")

    else:
        form = ClientPaymentForm()

    return render(request, "clients/create_payment.html", {"form": form})

@login_required
def edit_transaction(request, pk):

    choice_redirect = redirect_admin_to_user_choice(request)
    if choice_redirect:
        return choice_redirect

    effective_user = get_effective_user(request)
    is_admin = is_effective_admin(request)
    if is_admin:
        transaction = get_object_or_404(ProductTransaction, pk=pk)
    else:
        transaction = get_object_or_404(ProductTransaction, pk=pk, client__user=effective_user)

    if request.method == "POST":
        client_id = request.POST.get("client") or transaction.client_id
        form = ProductTransactionForm(request.POST, instance=transaction, client=client_id)

        if form.is_valid():
            form.save()
            return redirect("client_dashboard")

    else:
        form = ProductTransactionForm(instance=transaction, client=transaction.client_id)

    return render(request, "transactions/edit_transaction.html", {"form": form})


@login_required
def edit_payment(request, pk):

    choice_redirect = redirect_admin_to_user_choice(request)
    if choice_redirect:
        return choice_redirect

    effective_user = get_effective_user(request)
    is_admin = is_effective_admin(request)
    if is_admin:
        payment = get_object_or_404(Payment, pk=pk)
    else:
        payment = get_object_or_404(Payment, pk=pk, client__user=effective_user)

    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment) if is_admin else ClientPaymentForm(request.POST, instance=payment)

        if form.is_valid():
            form.save()
            return redirect("client_dashboard")

    else:
        form = PaymentForm(instance=payment) if is_admin else ClientPaymentForm(instance=payment)

    return render(request, "transactions/edit_payment.html", {"form": form})
