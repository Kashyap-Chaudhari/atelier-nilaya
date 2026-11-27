import json
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.serializers import serialize
from django.utils import timezone
from .models import AdminProfile, AdminAuditLog, TrashItem

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def format_inr(amount):
    """Formats a number into Indian Rupee representation (e.g. ₹2,45,000)."""
    try:
        val = round(float(amount))
        s = str(val)
        if len(s) <= 3:
            return f"₹{s}"
        last_three = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        return f"₹{','.join(groups)},{last_three}"
    except (ValueError, TypeError):
        return "₹0"

def admin_required(view_func):
    """Ensures the user is authenticated and authorized as staff or admin."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            try:
                from django.urls import reverse
                login_url = reverse('store_admin:login')
            except Exception:
                login_url = '/login/'
            return redirect(f'{login_url}?next={request.path}')
        if not (request.user.is_staff or request.user.is_superuser or hasattr(request.user, 'admin_profile')):
            messages.error(request, "Access restricted to authorized Atelier staff.")
            return redirect('store_admin:login')
        # Ensure AdminProfile exists
        if not hasattr(request.user, 'admin_profile'):
            AdminProfile.objects.create(
                user=request.user,
                role=AdminProfile.ROLE_SUPER_ADMIN if request.user.is_superuser else AdminProfile.ROLE_PRODUCT_MGR,
                display_title='Atelier Staff'
            )
        return view_func(request, *args, **kwargs)
    return _wrapped

def role_required(allowed_roles):
    """Enforces fine-grained role-based access control (RBAC)."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                try:
                    from django.urls import reverse
                    login_url = reverse('store_admin:login')
                except Exception:
                    login_url = '/login/'
                return redirect(f'{login_url}?next={request.path}')
            profile = getattr(request.user, 'admin_profile', None)
            if not profile and request.user.is_superuser:
                profile = AdminProfile.objects.create(
                    user=request.user,
                    role=AdminProfile.ROLE_SUPER_ADMIN,
                    display_title='Master Curator'
                )
            if not profile or not profile.is_active_staff:
                messages.error(request, "Your administrative account is inactive or not found.")
                return redirect('store_admin:login')
            if profile.role != AdminProfile.ROLE_SUPER_ADMIN and profile.role not in allowed_roles:
                messages.error(request, f"Access denied. Required permission: {', '.join(allowed_roles)}.")
                return redirect('store_admin:dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator

def log_audit(request, action, model_name, object_id, object_repr, changes_summary="", old_data=None, new_data=None):
    """Records an immutable audit trail entry."""
    try:
        AdminAuditLog.objects.create(
            user=request.user if request and request.user.is_authenticated else None,
            user_email=request.user.email if request and request.user.is_authenticated else "system",
            action=action,
            model_name=model_name,
            object_id=str(object_id),
            object_repr=str(object_repr)[:255],
            changes_summary=changes_summary,
            old_data_json=old_data or {},
            new_data_json=new_data or {},
            ip_address=get_client_ip(request) if request else None
        )
    except Exception as e:
        print(f"[Audit Log Warning]: {e}")

def move_to_trash(instance, user=None):
    """Safely archives an object to 30-day Trash before deleting from main table."""
    try:
        model_name = instance._meta.model_name
        obj_id = str(instance.pk)
        obj_repr = str(instance)
        serialized = json.loads(serialize('json', [instance]))[0]['fields']
        
        trash_item = TrashItem.objects.create(
            model_name=model_name,
            object_id=obj_id,
            object_repr=obj_repr,
            serialized_data=serialized,
            deleted_by=user
        )
        instance.delete()
        return trash_item
    except Exception as e:
        print(f"[Trash Archival Error]: {e}")
        instance.delete()
        return None
