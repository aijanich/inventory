from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import ProductTransaction, Payment
from .forms import ProductTransactionForm, PaymentForm, ClientPaymentForm
from django.shortcuts import render, redirect, get_object_or_404


@login_required
def create_transaction(request):

    if not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        raise PermissionDenied()

    if request.method == "POST":
        form = ProductTransactionForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("client_dashboard")

    else:
        form = ProductTransactionForm()

    return render(request, "transactions/create_transaction.html", {"form": form})

@login_required
def create_payment(request):

    if request.user.role != "client":
        raise PermissionDenied()

    if request.method == "POST":
        form = ClientPaymentForm(request.POST)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.client = request.user.profile
            payment.save()

            return redirect("client_dashboard")

    else:
        form = ClientPaymentForm()

    return render(request, "clients/create_payment.html", {"form": form})

@login_required
def edit_transaction(request, pk):

    is_admin = request.user.is_staff or getattr(request.user, "role", "") == "admin"
    if is_admin:
        transaction = get_object_or_404(ProductTransaction, pk=pk)
    else:
        transaction = get_object_or_404(ProductTransaction, pk=pk, client__user=request.user)

    if request.method == "POST":
        form = ProductTransactionForm(request.POST, instance=transaction)

        if form.is_valid():
            form.save()
            return redirect("client_dashboard")

    else:
        form = ProductTransactionForm(instance=transaction)

    return render(request, "transactions/edit_transaction.html", {"form": form})


@login_required
def edit_payment(request, pk):

    is_admin = request.user.is_staff or getattr(request.user, "role", "") == "admin"
    if is_admin:
        payment = get_object_or_404(Payment, pk=pk)
    else:
        payment = get_object_or_404(Payment, pk=pk, client__user=request.user)

    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment) if is_admin else ClientPaymentForm(request.POST, instance=payment)

        if form.is_valid():
            form.save()
            return redirect("client_dashboard")

    else:
        form = PaymentForm(instance=payment) if is_admin else ClientPaymentForm(instance=payment)

    return render(request, "transactions/edit_payment.html", {"form": form})
