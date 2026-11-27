from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from store_admin.models import AdminProfile, StoreSettings
from store_admin.utils import admin_required, log_audit, get_client_ip

def admin_login_view(request):
    try:
        dashboard_url = reverse('store_admin:dashboard')
    except Exception:
        dashboard_url = '/'

    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or hasattr(request.user, 'admin_profile')):
        return redirect(dashboard_url)

    store_settings = StoreSettings.get_settings()
    next_url = request.GET.get('next') or dashboard_url

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = None
        if '@' in username_or_email:
            matched_user = User.objects.filter(email__iexact=username_or_email).first()
            if matched_user:
                user = authenticate(request, username=matched_user.username, password=password)
        if not user:
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "This administrative account has been deactivated.")
                return render(request, 'store_admin/auth/login.html', {'store_settings': store_settings})

            profile, _ = AdminProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': AdminProfile.ROLE_SUPER_ADMIN if user.is_superuser else AdminProfile.ROLE_PRODUCT_MGR,
                    'display_title': 'Principal Curator'
                }
            )

            if not profile.is_active_staff and not user.is_superuser:
                messages.error(request, "Your administrative clearance has been paused by the Super Admin.")
                return render(request, 'store_admin/auth/login.html', {'store_settings': store_settings})

            login(request, user)
            profile.last_login_ip = get_client_ip(request)
            profile.save(update_fields=['last_login_ip'])

            log_audit(request, 'login', 'User', user.id, user.username, f"Staff login from {get_client_ip(request)}")

            messages.success(request, f"Welcome back, {user.first_name or user.username}. Sovereign console active.")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid administrator credentials. Please check your username and password.")

    return render(request, 'store_admin/auth/login.html', {
        'store_settings': store_settings,
        'next_url': next_url
    })

def admin_logout_view(request):
    if request.user.is_authenticated:
        log_audit(request, 'login', 'User', request.user.id, request.user.username, "Staff logged out")
    logout(request)
    messages.info(request, "You have been securely signed out of the Atelier Nilaya admin console.")
    return redirect('store_admin:login')

@admin_required
def admin_profile_view(request):
    profile = getattr(request.user, 'admin_profile', None)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_info':
            request.user.first_name = request.POST.get('first_name', '').strip()
            request.user.last_name = request.POST.get('last_name', '').strip()
            request.user.email = request.POST.get('email', '').strip()
            request.user.save()
            if profile:
                profile.phone = request.POST.get('phone', '').strip()
                profile.display_title = request.POST.get('display_title', '').strip()
                if 'avatar' in request.FILES:
                    profile.avatar = request.FILES['avatar']
                profile.save()
            messages.success(request, "Profile details updated successfully.")
            return redirect('/admin/profile/')

        elif action == 'change_password':
            old_p = request.POST.get('old_password', '')
            new_p = request.POST.get('new_password', '')
            confirm_p = request.POST.get('confirm_password', '')

            if not request.user.check_password(old_p):
                messages.error(request, "Current password verification failed.")
            elif len(new_p) < 8:
                messages.error(request, "New password must be at least 8 characters long.")
            elif new_p != confirm_p:
                messages.error(request, "New password confirmation does not match.")
            else:
                request.user.set_password(new_p)
                request.user.save()
                update_session_auth_hash(request, request.user)
                log_audit(request, 'update', 'User', request.user.id, request.user.username, "Password changed")
                messages.success(request, "Password changed successfully.")
                return redirect('/admin/profile/')

    return render(request, 'store_admin/auth/profile.html', {
        'profile': profile,
        'active_nav': 'settings'
    })
