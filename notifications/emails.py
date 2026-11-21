from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils import timezone
from .models import NotificationLog


def get_base_email_html(headline: str, body_content: str, cta_text: str = None, cta_url: str = None) -> str:
    """Returns an inline-styled, luxury HTML email body matching Atelier Nilaya aesthetic."""
    cta_block = ""
    if cta_text and cta_url:
        cta_block = f"""
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="margin: 32px 0 24px;">
            <tr>
                <td align="center" style="border-radius: 6px; background-color: #d9b56b;">
                    <a href="{cta_url}" target="_blank" style="display: inline-block; padding: 14px 32px; font-family: 'Manrope', Arial, sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: #1c0b13; text-decoration: none; border-radius: 6px;">
                        {cta_text} &rarr;
                    </a>
                </td>
            </tr>
        </table>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{headline}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0d0c0a; font-family: 'Manrope', Arial, sans-serif; color: #f8f5f0; -webkit-font-smoothing: antialiased;">
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #0d0c0a; padding: 40px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #1c0b13; border: 1px solid rgba(217, 181, 107, 0.35); border-radius: 8px; overflow: hidden; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);">
          <!-- Atelier Header Banner -->
          <tr>
            <td align="center" style="padding: 36px 32px 24px; border-bottom: 1px solid rgba(217, 181, 107, 0.2);">
              <span style="font-family: 'Manrope', Arial, sans-serif; font-size: 11px; letter-spacing: 0.28em; text-transform: uppercase; color: #d9b56b; font-weight: 700;">ATELIER NILAYA &bull; SURAT</span>
              <h1 style="margin: 12px 0 0; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 26px; font-weight: 400; color: #f8f5f0; letter-spacing: 0.04em;">
                {headline}
              </h1>
            </td>
          </tr>
          
          <!-- Content Body -->
          <tr>
            <td style="padding: 36px 36px 28px; font-size: 15px; line-height: 1.7; color: rgba(248, 245, 240, 0.88);">
              {body_content}
              {cta_block}
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding: 24px 36px 32px; background-color: #14070e; border-top: 1px solid rgba(217, 181, 107, 0.15); text-align: center; font-size: 12px; line-height: 1.6; color: rgba(248, 245, 240, 0.5);">
              <p style="margin: 0 0 6px; color: #d9b56b;">Atelier Nilaya Private Jewellery Vault &bull; Established 1954</p>
              <p style="margin: 0;">Ghod Dod Road, Surat, Gujarat 395007 &bull; Concierge: +91 98251 00000</p>
              <p style="margin: 8px 0 0; font-size: 11px;">If you did not initiate this request, please contact our confidential concierge immediately.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def send_verification_email(user, request=None) -> bool:
    """Generates verification link and dispatches verification email to patron."""
    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        domain = request.get_host() if request else "127.0.0.1:8000"
        scheme = "https" if request and request.is_secure() else "http"
        verify_url = f"{scheme}://{domain}/verify-email/{uid}/{token}/"

        headline = "Verify Your Atelier Client Folio"
        salutation = f"Esteemed Patron {user.first_name or user.username},"
        body = f"""
        <p style="margin-top: 0;">{salutation}</p>
        <p>Thank you for initiating your private acquisition folio at Atelier Nilaya. To unlock seamless private checkout and secure delivery tracking for certified haute joaillerie, please verify your email address below.</p>
        <p style="font-size: 13px; color: #d9b56b; margin-top: 16px;">This verification link is confidential, single-use, and expires in 1 hour.</p>
        """

        html_content = get_base_email_html(headline, body, cta_text="Verify My Email", cta_url=verify_url)
        plain_text = f"""{headline}
{salutation}

Thank you for initiating your private folio at Atelier Nilaya.
Please visit the following link within 1 hour to verify your email and unlock boutique checkout:

{verify_url}

Atelier Nilaya Haute Joaillerie, Surat
"""
        msg = EmailMultiAlternatives(
            subject="Verify Your Email • Atelier Nilaya Haute Joaillerie",
            body=plain_text,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'Atelier Nilaya <concierge@ateliernilaya.com>'),
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        NotificationLog.objects.create(
            channel='email',
            template_name='email_verification',
            recipient=user.email,
            status='sent',
            message_payload=f"Verification link sent: {verify_url}",
            sent_at=timezone.now()
        )
        return True
    except Exception as e:
        NotificationLog.objects.create(
            channel='email',
            template_name='email_verification',
            recipient=user.email,
            status='failed',
            error_message=str(e)
        )
        return False


def send_password_reset_email(user, request=None) -> bool:
    """Sends confidential password reset link to customer."""
    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        domain = request.get_host() if request else "127.0.0.1:8000"
        scheme = "https" if request and request.is_secure() else "http"
        reset_url = f"{scheme}://{domain}/reset/{uid}/{token}/"

        headline = "Confidential Password Reset"
        salutation = f"Hello {user.first_name or user.username},"
        body = f"""
        <p style="margin-top: 0;">{salutation}</p>
        <p>A request was received to reset the authentication password for your Atelier Nilaya account.</p>
        <p>Click the button below to establish a new password. For your protection, this secure link is valid for <strong>1 hour</strong> and can only be used once.</p>
        <p style="font-size: 13px; color: rgba(248, 245, 240, 0.65); margin-top: 16px;">If you did not request a password reset, you can safely disregard this message; your credentials remain secure.</p>
        """

        html_content = get_base_email_html(headline, body, cta_text="Set New Password", cta_url=reset_url)
        plain_text = f"""{headline}
{salutation}

A request was received to reset your Atelier Nilaya password.
Please visit the link below within 1 hour to set a new password:

{reset_url}

If you did not request this, please ignore this email.
Atelier Nilaya Haute Joaillerie
"""
        msg = EmailMultiAlternatives(
            subject="Confidential Password Reset • Atelier Nilaya",
            body=plain_text,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'Atelier Nilaya <concierge@ateliernilaya.com>'),
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        NotificationLog.objects.create(
            channel='email',
            template_name='password_reset',
            recipient=user.email,
            status='sent',
            message_payload=f"Password reset link sent: {reset_url}",
            sent_at=timezone.now()
        )
        return True
    except Exception as e:
        NotificationLog.objects.create(
            channel='email',
            template_name='password_reset',
            recipient=user.email,
            status='failed',
            error_message=str(e)
        )
        return False


def send_password_changed_notification(user) -> bool:
    """Dispatches a security notification stating password was changed."""
    try:
        headline = "Your Password Has Been Updated"
        salutation = f"Hello {user.first_name or user.username},"
        body = f"""
        <p style="margin-top: 0;">{salutation}</p>
        <p>This is a formal confirmation that the password for your Atelier Nilaya patron account was recently changed.</p>
        <p>All other active browsing sessions on any other devices have been securely terminated.</p>
        <p style="font-size: 13px; color: #d9b56b; margin-top: 18px;">If you did not authorize this change, please contact our confidential concierge desk immediately at <strong>+91 98251 00000</strong>.</p>
        """

        html_content = get_base_email_html(headline, body)
        plain_text = f"""{headline}
{salutation}

The password for your Atelier Nilaya account has been successfully updated. All other active sessions have been terminated.
If you did not authorize this, please reach our concierge desk immediately.

Atelier Nilaya Haute Joaillerie
"""
        msg = EmailMultiAlternatives(
            subject="Security Alert: Your Password Was Changed • Atelier Nilaya",
            body=plain_text,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'Atelier Nilaya <concierge@ateliernilaya.com>'),
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        NotificationLog.objects.create(
            channel='email',
            template_name='password_changed_alert',
            recipient=user.email,
            status='sent',
            message_payload="Password changed security notice sent.",
            sent_at=timezone.now()
        )
        return True
    except Exception as e:
        return False


def send_welcome_email(user) -> bool:
    """Sends celebratory welcome note after email verification."""
    try:
        headline = "Welcome to Atelier Nilaya"
        salutation = f"Welcome, {user.first_name or user.username},"
        body = f"""
        <p style="margin-top: 0;">{salutation}</p>
        <p>Your client folio has been authenticated. You now have full access to our curated private editions, benchmark bullion pricing, and bespoke heirloom acquisitions.</p>
        <p>Every piece is accompanied by a tamper-proof digital hallmark registry and white-glove insured transit across India.</p>
        """

        html_content = get_base_email_html(headline, body, cta_text="Explore Curated Editions", cta_url="http://127.0.0.1:8000/vault/")
        plain_text = f"""{headline}
{salutation}

Your client folio has been verified. You now have full access to private acquisitions at Atelier Nilaya.
Visit our vault: http://127.0.0.1:8000/vault/

Atelier Nilaya Haute Joaillerie, Surat
"""
        msg = EmailMultiAlternatives(
            subject="Welcome to Atelier Nilaya • Client Folio Activated",
            body=plain_text,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'Atelier Nilaya <concierge@ateliernilaya.com>'),
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        NotificationLog.objects.create(
            channel='email',
            template_name='welcome_folio',
            recipient=user.email,
            status='sent',
            message_payload="Welcome folio activated notice sent.",
            sent_at=timezone.now()
        )
        return True
    except Exception as e:
        return False
