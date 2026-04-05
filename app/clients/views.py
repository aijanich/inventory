from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.core.paginator import Paginator
from transactions.models import ProductTransaction, Payment
from clients.models import ClientProfile
from transactions.forms import ClientPaymentForm
from products.models import Product
from colors.models import Color
from products.forms import ProductForm
from colors.forms import ColorForm


@login_required
def client_dashboard(request):

    is_admin = request.user.is_staff or getattr(request.user, "role", "") == "admin"
    if not hasattr(request.user, "profile") and not is_admin:
        return redirect("login")

    if is_admin:
        selected_client_id = request.GET.get("client")
        clients = (
            ClientProfile.objects.select_related("user")
            .exclude(user__is_staff=True)
            .order_by("user__username")
        )
        transactions = ProductTransaction.objects.select_related("client", "product", "color").all()
        payments = Payment.objects.select_related("client", "client__user").all()
        if selected_client_id:
            transactions = transactions.filter(client_id=selected_client_id)
            payments = payments.filter(client_id=selected_client_id)
    else:
        profile = request.user.profile
        transactions = ProductTransaction.objects.filter(client=profile).select_related("product", "color")
        payments = Payment.objects.filter(client=profile).select_related("client")

    total_products = transactions.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    total_payments = payments.aggregate(
        total=Sum("amount")
    )["total"] or 0

    balance = total_products - total_payments

    context = {
        "transactions": transactions.order_by("-date")[:10],
        "payments": payments.order_by("-date")[:10],
        "total_products": total_products,
        "total_payments": total_payments,
        "balance": balance,
    }
    if is_admin:
        context["clients"] = clients
        context["selected_client_id"] = selected_client_id

    return render(request, "clients/dashboard.html", context)


@login_required
def dashboard_products(request):

    if not hasattr(request.user, "profile") and not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        return redirect("login")

    products = Product.objects.order_by("-created_at")
    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "clients/products.html",
        {"products": page_obj.object_list, "page_obj": page_obj},
    )


@login_required
def dashboard_colors(request):

    if not hasattr(request.user, "profile") and not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        return redirect("login")

    colors = Color.objects.order_by("-created_at")
    paginator = Paginator(colors, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "clients/colors.html",
        {"colors": page_obj.object_list, "page_obj": page_obj},
    )


@login_required
def dashboard_product_create(request):

    if not hasattr(request.user, "profile") and not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        return redirect("login")

    if not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        raise PermissionDenied()

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("dashboard_products")

    else:
        form = ProductForm()

    return render(request, "clients/create_product.html", {"form": form})


@login_required
def dashboard_color_create(request):

    if not hasattr(request.user, "profile") and not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        return redirect("login")

    if not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        raise PermissionDenied()

    if request.method == "POST":
        form = ColorForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("dashboard_colors")

    else:
        form = ColorForm()

    return render(request, "clients/create_color.html", {"form": form})


@login_required
def dashboard_payments(request):

    if not hasattr(request.user, "profile") and not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        return redirect("login")

    payments = Payment.objects.select_related("client", "client__user").order_by("-date")
    if not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        payments = payments.filter(client__user=request.user)
    paginator = Paginator(payments, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "clients/payments.html",
        {"payments": page_obj.object_list, "page_obj": page_obj},
    )


@login_required
def dashboard_payment_create(request):

    if not hasattr(request.user, "profile") and not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        return redirect("login")

    if getattr(request.user, "role", "") != "client":
        raise PermissionDenied()

    if request.method == "POST":
        form = ClientPaymentForm(request.POST)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.client = request.user.profile
            payment.save()
            return redirect("dashboard_payments")

    else:
        form = ClientPaymentForm()

    return render(request, "clients/create_payment.html", {"form": form})


@login_required
def dashboard_product_edit(request, pk):

    if not hasattr(request.user, "profile") and not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        return redirect("admin:index")  # yoki login sahifaga

    if not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        raise PermissionDenied()

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            return redirect("dashboard_products")

    else:
        form = ProductForm(instance=product)

    return render(request, "clients/edit_product.html", {"form": form, "product": product})


@login_required
def dashboard_color_edit(request, pk):

    if not hasattr(request.user, "profile") and not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        return redirect("admin:index")  # yoki login sahifaga

    if not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        raise PermissionDenied()

    color = get_object_or_404(Color, pk=pk)

    if request.method == "POST":
        form = ColorForm(request.POST, instance=color)

        if form.is_valid():
            form.save()
            return redirect("dashboard_colors")

    else:
        form = ColorForm(instance=color)

    return render(request, "clients/edit_color.html", {"form": form, "color": color})
