# Email Function (Enterprise-Ready)

# Importation des classes et fonctions nécessaires pour la verification d'inscription
from django.template.loader import render_to_string  # Charge et rend un template HTML avec des variables
from django.core.mail import EmailMultiAlternatives, send_mail # (recommandé -> UTF-8 pour les caractères non-ASCII)
from django.conf import settings
from django.utils.html import strip_tags


def send_order_confirmation_email(order):
    """
    Sends an order confirmation email to the customer.
    Enterprise-grade transactional email.
    """

    if not order.user.email:
        return  # Fail silently (common practice)

    subject = f"🧾 Order Confirmation – {order.order_number}"

    from_email = settings.DEFAULT_FROM_EMAIL
    to = [order.user.email]

    # ───────────────────────────────
    # Template Context
    # ───────────────────────────────
    context = {
        "order": order,
        "user": order.user,
        "items": order.items.all(),
        "company_name": settings.COMPANY_NAME,
        "support_email": settings.SUPPORT_EMAIL,
    }

    # ───────────────────────────────
    # Render Templates
    # ───────────────────────────────
    html_content = render_to_string(
        "emails/order_confirmation.html",
        context
    )

    text_content = strip_tags(html_content)

    # ───────────────────────────────
    # Build Email
    # ───────────────────────────────
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=to,
    )

    email.attach_alternative(html_content, "text/html")

    # ───────────────────────────────
    # Send
    # ───────────────────────────────
    email.send(fail_silently=False)

    

def send_order_notification_simple_email(order):
    """
    Sends a simple order confirmation email to the customer.
    Basic transactional email (using send_mail).
    """
    if not order.user.email:
        return  # Fail silently (common practice)

    subject = f"🧾 Order Confirmation - {order.order_number} is received"
    message = f"""
        Hello {order.user.first_name},\n\n
        Your order has been received successfully.\n\n
        Thank you for your order {order.order_number}.\n\n
        Total Amount: {order.total_amount} {order.currency}\n\n
        We appreciate your business!
        """
    from_email = settings.DEFAULT_FROM_EMAIL
    # recipient_list = [order.user.email]
    to = [order.user.email]

    send_mail(
        subject,
        message,
        from_email,
        to,
        fail_silently=False,
    )