from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from clients.models import ClientProfile
from .forms import ClientUserCreateForm, ClientUserUpdateForm
from .models import User


def _require_admin(request):
    is_admin = request.user.is_staff or getattr(request.user, "role", "") == "admin"
    if not is_admin:
        raise PermissionDenied()


@login_required
def dashboard_users(request):
    _require_admin(request)

    qs = (
        User.objects.filter(role="client")
        .select_related("profile")
        .order_by("-id")
    )
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "users/users.html",
        {"users": page_obj.object_list, "page_obj": page_obj},
    )


@login_required
def dashboard_user_create(request):
    _require_admin(request)

    if request.method == "POST":
        form = ClientUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard_users")
    else:
        form = ClientUserCreateForm()
    return render(request, "users/user_form.html", {"form": form, "mode": "create"})


@login_required
def dashboard_user_edit(request, pk: int):
    _require_admin(request)

    user = get_object_or_404(User, pk=pk, role="client")
    profile = getattr(user, "profile", None)
    if profile is None:
        # Be defensive: in case legacy users exist without a profile row.
        profile = ClientProfile.objects.create(user=user, phone="", address="")

    if request.method == "POST":
        form = ClientUserUpdateForm(request.POST, instance=user, profile=profile)
        if form.is_valid():
            form.save()
            return redirect("dashboard_users")
    else:
        form = ClientUserUpdateForm(instance=user, profile=profile)

    return render(
        request,
        "users/user_form.html",
        {"form": form, "mode": "edit", "user_obj": user},
    )

