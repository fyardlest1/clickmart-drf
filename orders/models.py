# orders/models.py
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from products.models import Product


# User = settings.AUTH_USER_MODEL
User = get_user_model()


class Order(models.Model):
    """
    Enterprise-grade Order model.
    Represents a finalized or in-progress purchase transaction.
    """

    # ───────────────────────────────
    # Order Status Lifecycle
    # ───────────────────────────────
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('COMPLETED', 'Completed'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
        ('FAILED', 'Failed'),
    ]    

    # ───────────────────────────────
    # Primary Identifiers
    # ───────────────────────────────
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=32, unique=True, db_index=True, help_text="Human-readable order reference")

    # ───────────────────────────────
    # Ownership
    # ───────────────────────────────
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")

    # ───────────────────────────────
    # Status & Lifecycle
    # ───────────────────────────────
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT", db_index=True)

    # ───────────────────────────────
    # Financial Fields (IMMUTABLE)
    # ───────────────────────────────
    currency = models.CharField(max_length=3, default="USD")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Final amount charged (subtotal + tax + shipping - discounts)"
    )

    # ───────────────────────────────
    # Payment Metadata
    # ───────────────────────────────
    payment_provider = models.CharField(max_length=50, blank=True, null=True, help_text="Stripe, PayPal, etc.")
    payment_reference = models.CharField(max_length=255, blank=True, null=True, help_text="Provider transaction ID")
    paid_at = models.DateTimeField(blank=True, null=True)

    # ───────────────────────────────
    # Shipping & Billing (Snapshot)
    # ───────────────────────────────
    # billing_address = models.JSONField(
    #     blank=True,
    #     null=True,
    #     help_text="Snapshot of billing address at purchase time"
    # )

    shipping_address = models.JSONField(
        blank=True,
        null=True,
        help_text="Snapshot of shipping address at purchase time"
    )
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Contact phone number for the order")
    city = models.CharField(max_length=50, blank=True, null=True, help_text="City for the shipping address")
    state = models.CharField(max_length=50, blank=True, null=True, help_text="State for the shipping address")
    postal_code = models.CharField(max_length=20, blank=True, null=True, help_text="Postal code for the shipping address")
    country = models.CharField(max_length=50, blank=True, null=True, default="Canada", help_text="Country for the shipping address")

    # ───────────────────────────────
    # Audit & Metadata
    # ───────────────────────────────
    notes = models.TextField(blank=True, help_text="Internal notes (admin only)")
    metadata = models.JSONField(blank=True, null=True, help_text="Flexible storage for integrations & analytics")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ───────────────────────────────
    # Database Optimizations
    # ───────────────────────────────
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user"]),
        ]

    # ───────────────────────────────
    # Business Logic
    # ───────────────────────────────
    # Order totals should be derived from OrderItems once, then frozen.
    def recalculate_from_items(self):
        """
        Recalculate financial totals.
        Should be called ONLY before payment.
        """
        self.subtotal = sum(item.unit_price * item.quantity for item in self.items.all())
        self.tax_amount = sum(item.tax_amount for item in self.items.all())
        self.total_amount = (
            self.subtotal
            + self.tax_amount
            + self.shipping_amount
            - self.discount_amount
        )


    def mark_as_paid(self, provider: str, reference: str):
        """
        Safely mark order as paid.
        """
        self.status = self.Status.PAID
        self.payment_provider = provider
        self.payment_reference = reference
        self.paid_at = timezone.now()
        self.save(update_fields=[
            "status",
            "payment_provider",
            "payment_reference",
            "paid_at"
        ])        
    
    # guarantee order_number creation
    # def save(self, *args, **kwargs):
    #     if not self.order_number:
    #         self.order_number = (
    #             f"ORD-"
    #             f"{timezone.now().strftime('%Y%m%d')}-"
    #             f"{uuid.uuid4().hex[:6].upper()}"
    #         )
    #     super().save(*args, **kwargs)

    def __str__(self):
        # f"{self.id} x {self.user.email}"
        return f"Order {self.order_number} ({self.status})"


class OrderItem(models.Model):
    """
    Immutable snapshot of a product at the time of purchase.
    """

    # ───────────────────────────────
    # Relations
    # ───────────────────────────────
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    # Optional reference (DO NOT rely on it for pricing)
    product = models.ForeignKey(
        Product, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name="order_items", 
        help_text="Optional reference for analytics only"
    )

    # ───────────────────────────────
    # Product Snapshot (IMMUTABLE)
    # ───────────────────────────────
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.TextField(blank=True)

    # ───────────────────────────────
    # Pricing Snapshot
    # ───────────────────────────────
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    tax_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        # Prevent invalid values like -10 or 500
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        help_text="Tax percent applied at purchase time"
    )

    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Final line total INCLUDING tax & discounts"
    )

    # ───────────────────────────────
    # Audit
    # ───────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)

    # ───────────────────────────────
    # Database Optimizations
    # ───────────────────────────────
    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
        ]

    # ───────────────────────────────
    # Business Logic
    # ───────────────────────────────
    def calculate_totals(self):
        """
        Calculate tax and line total.
        MUST be called before saving.
        """
        base_price = self.unit_price * self.quantity
        self.tax_amount = (base_price * self.tax_percent) / Decimal("100")
        self.line_total = base_price + self.tax_amount - self.discount_amount

    def save(self, *args, **kwargs):
        """
        Enforce immutability after order is paid.
        """
        if self.pk and self.order.status not in [
            self.order.Status.DRAFT,
            self.order.Status.PENDING,
        ]:
            raise ValueError("Order items cannot be modified after payment.")

        # Always check for None, not falsy decimals
        if self.line_total is None:
            self.calculate_totals()

        super().save(*args, **kwargs)

    def __str__(self):        
        return f"{self.quantity} x {self.product_name}"


# Refund System (Order + Line-Item Level)
class Refund(models.Model):
    """
    Represents a refund transaction (partial or full).
    """

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="refunds")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    reason = models.TextField(blank=True)
    payment_provider = models.CharField(max_length=50, help_text="Stripe, PayPal, etc.")
    provider_reference = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    processed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def mark_completed(self, provider_ref: str):
        self.status = self.Status.COMPLETED
        self.provider_reference = provider_ref
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "provider_reference", "processed_at"])

    def __str__(self):
        return f"Refund {self.amount} ({self.status})"


# Line-item refunds (audit-safe)
class RefundItem(models.Model):
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, related_name="items")
    order_item = models.ForeignKey(OrderItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)



