from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta, date
from urllib.parse import urlencode
import csv
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

    date_preset = request.GET.get("date_preset", "")
    start_date_raw = request.GET.get("start_date", "")
    end_date_raw = request.GET.get("end_date", "")

    def parse_date(value):
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    def apply_date_filter(queryset):
        start_date = parse_date(start_date_raw)
        end_date = parse_date(end_date_raw)
        if start_date or end_date:
            if start_date and end_date:
                return queryset.filter(date__range=(start_date, end_date))
            if start_date:
                return queryset.filter(date__gte=start_date)
            return queryset.filter(date__lte=end_date)

        today = timezone.localdate()
        if date_preset == "today":
            return queryset.filter(date=today)
        if date_preset == "yesterday":
            return queryset.filter(date=today - timedelta(days=1))
        if date_preset == "week":
            start = today - timedelta(days=today.weekday())
            return queryset.filter(date__range=(start, today))
        if date_preset == "month":
            start = today.replace(day=1)
            return queryset.filter(date__range=(start, today))
        return queryset

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

    transactions = apply_date_filter(transactions)
    payments = apply_date_filter(payments)

    total_products = transactions.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    total_payments = payments.aggregate(
        total=Sum("amount")
    )["total"] or 0

    balance = total_products - total_payments

    context = {
        "transactions": transactions.order_by("-id")[:10],
        "payments": payments.order_by("-id")[:10],
        "total_products": total_products,
        "total_payments": total_payments,
        "balance": balance,
    }
    if is_admin:
        context["clients"] = clients
        context["selected_client_id"] = selected_client_id
    context["date_preset"] = date_preset
    context["start_date"] = start_date_raw
    context["end_date"] = end_date_raw
    export_params = {}
    if is_admin and selected_client_id:
        export_params["client"] = selected_client_id
    if date_preset:
        export_params["date_preset"] = date_preset
    if start_date_raw:
        export_params["start_date"] = start_date_raw
    if end_date_raw:
        export_params["end_date"] = end_date_raw
    context["export_query"] = urlencode(export_params)

    return render(request, "clients/dashboard.html", context)


@login_required
def dashboard_products(request):

    if not hasattr(request.user, "profile") and not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        return redirect("login")

    products = Product.objects.order_by("-id")
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

    colors = Color.objects.order_by("-id")
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
        form = ColorForm(request.POST, request.FILES)

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

    payments = Payment.objects.select_related("client", "client__user").order_by("-id")
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
        return redirect("login")

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
        return redirect("login")

    if not (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
        raise PermissionDenied()

    color = get_object_or_404(Color, pk=pk)

    if request.method == "POST":
        form = ColorForm(request.POST, request.FILES, instance=color)

        if form.is_valid():
            form.save()
            return redirect("dashboard_colors")

    else:
        form = ColorForm(instance=color)

    return render(request, "clients/edit_color.html", {"form": form, "color": color})


@login_required
def export_transactions_csv(request):

    is_admin = request.user.is_staff or getattr(request.user, "role", "") == "admin"
    if not is_admin and not hasattr(request.user, "profile"):
        return redirect("login")

    selected_client_id = request.GET.get("client")
    date_preset = request.GET.get("date_preset", "")
    start_date_raw = request.GET.get("start_date", "")
    end_date_raw = request.GET.get("end_date", "")

    def parse_date(value):
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    def apply_date_filter(queryset):
        start_date = parse_date(start_date_raw)
        end_date = parse_date(end_date_raw)
        if start_date or end_date:
            if start_date and end_date:
                return queryset.filter(date__range=(start_date, end_date))
            if start_date:
                return queryset.filter(date__gte=start_date)
            return queryset.filter(date__lte=end_date)

        today = timezone.localdate()
        if date_preset == "today":
            return queryset.filter(date=today)
        if date_preset == "yesterday":
            return queryset.filter(date=today - timedelta(days=1))
        if date_preset == "week":
            start = today - timedelta(days=today.weekday())
            return queryset.filter(date__range=(start, today))
        if date_preset == "month":
            start = today.replace(day=1)
            return queryset.filter(date__range=(start, today))
        return queryset
    transactions = ProductTransaction.objects.select_related("client", "product", "color").order_by("-id")
    if is_admin and selected_client_id:
        transactions = transactions.filter(client_id=selected_client_id)
    elif not is_admin:
        transactions = transactions.filter(client__user=request.user)
    transactions = apply_date_filter(transactions)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="transactions.csv"'
    writer = csv.writer(response)
    writer.writerow(["Sana", "Mijoz", "Tovar", "Rang", "Soni", "Narxi", "Summasi"])
    for t in transactions:
        writer.writerow([
            t.date.strftime("%d.%m.%Y") if t.date else "",
            str(t.client),
            t.product.name if t.product else "",
            str(t.color) if t.color else "",
            f"{t.quantity:.2f}",
            f"{t.price:.2f}" if t.price is not None else "",
            f"{t.total_amount:.2f}" if t.total_amount is not None else "",
        ])
    return response


@login_required
def export_transactions_pdf(request):

    is_admin = request.user.is_staff or getattr(request.user, "role", "") == "admin"
    if not is_admin and not hasattr(request.user, "profile"):
        return redirect("login")

    selected_client_id = request.GET.get("client")
    date_preset = request.GET.get("date_preset", "")
    start_date_raw = request.GET.get("start_date", "")
    end_date_raw = request.GET.get("end_date", "")

    def parse_date(value):
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    def apply_date_filter(queryset):
        start_date = parse_date(start_date_raw)
        end_date = parse_date(end_date_raw)
        if start_date or end_date:
            if start_date and end_date:
                return queryset.filter(date__range=(start_date, end_date))
            if start_date:
                return queryset.filter(date__gte=start_date)
            return queryset.filter(date__lte=end_date)

        today = timezone.localdate()
        if date_preset == "today":
            return queryset.filter(date=today)
        if date_preset == "yesterday":
            return queryset.filter(date=today - timedelta(days=1))
        if date_preset == "week":
            start = today - timedelta(days=today.weekday())
            return queryset.filter(date__range=(start, today))
        if date_preset == "month":
            start = today.replace(day=1)
            return queryset.filter(date__range=(start, today))
        return queryset
    transactions = ProductTransaction.objects.select_related("client", "product", "color").order_by("-id")
    if is_admin and selected_client_id:
        transactions = transactions.filter(client_id=selected_client_id)
    elif not is_admin:
        transactions = transactions.filter(client__user=request.user)
    transactions = apply_date_filter(transactions)

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="transactions.pdf"'
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, height - 40, "Oxirgi tovarlar eksporti")
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, height - 55, timezone.now().strftime("%d.%m.%Y %H:%M"))

    y = height - 80
    pdf.setFont("Helvetica-Bold", 8)
    headers = ["Sana", "Mijoz", "Tovar", "Rang", "Soni", "Narxi", "Summasi"]
    x_positions = [40, 90, 170, 270, 340, 390, 450]
    for i, h in enumerate(headers):
        pdf.drawString(x_positions[i], y, h)
    y -= 12
    pdf.setFont("Helvetica", 8)

    for t in transactions:
        if y < 40:
            pdf.showPage()
            y = height - 40
            pdf.setFont("Helvetica-Bold", 8)
            for i, h in enumerate(headers):
                pdf.drawString(x_positions[i], y, h)
            y -= 12
            pdf.setFont("Helvetica", 8)

        pdf.drawString(x_positions[0], y, t.date.strftime("%d.%m.%Y") if t.date else "")
        pdf.drawString(x_positions[1], y, str(t.client)[:12])
        pdf.drawString(x_positions[2], y, (t.product.name if t.product else "")[:16])
        pdf.drawString(x_positions[3], y, (str(t.color) if t.color else "")[:8])
        pdf.drawRightString(x_positions[4] + 25, y, f"{t.quantity:.2f}")
        pdf.drawRightString(x_positions[5] + 35, y, f"{t.price:.2f}" if t.price is not None else "")
        pdf.drawRightString(x_positions[6] + 50, y, f"{t.total_amount:.2f}" if t.total_amount is not None else "")
        y -= 12

    pdf.showPage()
    pdf.save()
    return response
