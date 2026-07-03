from django.contrib.auth import get_user_model
from django.shortcuts import redirect


ACTING_USER_SESSION_KEY = "acting_user_id"


def is_real_admin(user):
    return user.is_authenticated and (
        user.is_staff or getattr(user, "role", "") == "admin"
    )


def is_admin_user(user):
    return user.is_staff or getattr(user, "role", "") == "admin"


def ordinary_users():
    return (
        get_user_model()
        .objects.filter(role="client", is_staff=False)
        .order_by("username")
    )


def get_effective_user(request):
    if not request.user.is_authenticated:
        return request.user

    if not is_real_admin(request.user):
        return request.user

    acting_user_id = request.session.get(ACTING_USER_SESSION_KEY)
    if not acting_user_id:
        return request.user

    try:
        return ordinary_users().get(pk=acting_user_id)
    except get_user_model().DoesNotExist:
        request.session.pop(ACTING_USER_SESSION_KEY, None)
        return request.user


def is_effective_admin(request):
    return is_admin_user(get_effective_user(request))


def admin_needs_user_choice(request):
    return is_real_admin(request.user) and not request.session.get(ACTING_USER_SESSION_KEY)


def redirect_admin_to_user_choice(request):
    if admin_needs_user_choice(request):
        return redirect("admin_user_select")
    return None


def acting_context(request):
    effective_user = get_effective_user(request)
    return {
        "effective_user": effective_user,
        "effective_is_admin": is_admin_user(effective_user),
        "is_acting_user": (
            request.user.is_authenticated
            and effective_user.is_authenticated
            and request.user.pk != effective_user.pk
        ),
    }
