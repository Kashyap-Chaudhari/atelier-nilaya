from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
from .models import UserProfile


class EmailOrPhoneBackend(ModelBackend):
    """
    Authoritative authentication backend for Atelier Nilaya.
    Allows authentication via Email address or Indian Mobile number with standard hashed passwords.
    Integrates brute-force lockout tracking on the UserProfile model.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        identifier = str(username).strip()
        user = None

        # Clean mobile number if input looks like a phone number
        cleaned_phone = identifier.replace(' ', '').replace('-', '')
        if cleaned_phone.startswith('+91'):
            cleaned_phone = cleaned_phone[3:]
        elif cleaned_phone.startswith('0') and len(cleaned_phone) == 11:
            cleaned_phone = cleaned_phone[1:]

        if '@' in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
        elif cleaned_phone.isdigit() and len(cleaned_phone) == 10:
            # Match by profile mobile number or username
            profile = UserProfile.objects.filter(mobile_number=cleaned_phone).select_related('user').first()
            if profile:
                user = profile.user
            else:
                user = User.objects.filter(
                    Q(username=cleaned_phone) |
                    Q(username=f"+91{cleaned_phone}") |
                    Q(last_name=cleaned_phone)
                ).first()

        if not user:
            user = User.objects.filter(username__iexact=identifier).first()

        if not user:
            return None

        profile, _ = UserProfile.objects.get_or_create(user=user)

        # Check account lockout
        if profile.is_locked():
            if request is not None:
                request.account_locked = True
                request.locked_minutes = profile.get_lock_minutes_remaining()
            return None

        # Check password hash
        if user.check_password(password) and self.user_can_authenticate(user):
            profile.reset_failed_attempts()
            return user
        else:
            profile.register_failed_attempt()
            if profile.is_locked() and request is not None:
                request.account_locked = True
                request.locked_minutes = 15
            return None
