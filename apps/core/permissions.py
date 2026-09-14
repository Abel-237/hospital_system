from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin
from rest_framework import permissions
from django.utils.translation import gettext_lazy as _

def role_required(*allowed_roles):
    """
    Decorator for views that checks whether a user has one of the allowed roles.
    Superusers automatically bypass role checks.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
                
            raise PermissionDenied(_("Accès refusé: vous n'avez pas le rôle requis pour cette action."))
        return _wrapped_view
    return decorator


class RoleRequiredMixin(AccessMixin):
    """
    Verify that the current user has one of the specified roles.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if hasattr(request.user, 'role') and request.user.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied(_("Accès refusé: vous n'avez pas le rôle requis pour cette action."))


class HasRolePermission(permissions.BasePermission):
    """
    DRF permission class to verify user role against allowed_roles defined on the view.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        allowed_roles = getattr(view, 'allowed_roles', None)
        if allowed_roles is None:
            return True
        return hasattr(request.user, 'role') and request.user.role in allowed_roles
