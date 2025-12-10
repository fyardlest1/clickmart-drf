import uuid
from decimal import Decimal
from django.db import models
from django.utils.text import slugify


class Product(models.Model):
    """
    A production-ready Product model suitable for e-commerce,
    inventory management, or catalog applications.
    """

    # Unique ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Leave empty if no discount"
    )

    # Inventory
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Images
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    # Categorization
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Optional category (e.g., Drinks, Clothes, Electronics)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True) # only at created time, can not be changed later (created once)
    updated_at = models.DateTimeField(auto_now=True) # can be change anytime

    # Auto-generate slug
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Ensure unique slug
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    # Price utility
    @property
    def final_price(self):
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    def __str__(self):
        return self.name
