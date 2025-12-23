# carts/models.py
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from decimal import Decimal

# get the user
User = get_user_model()


class Cart(models.Model):
    """
    Cart belongs to a user.
    A user has only one active cart.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart({self.user})"
    
    """
    You should NOT store totals in the database
    """
    
    # Total price before tax for all items
    @property  # (can be use everywhere)
    def subtotal(self):
        return sum(
            (item.product.final_price * item.quantity)
            for item in self.items.all()
        )

    # Total tax amount for the entire cart.
    @property  # (can be use everywhere)
    def tax_total(self):
        return sum(
            (
                (item.product.final_price * item.product.tax_percent) / Decimal("100")
            ) * item.quantity
            for item in self.items.all()
        )

    # Final cart amount (clean design: cart delegates to item logic).
    @property  # (can be use everywhere)
    def total(self):
        return sum(item.subtotal for item in self.items.all())
    

class CartItem(models.Model):
    """
    Each item inside the cart.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        # Never trust frontend tax calculations.
        return self.product.price_with_tax * self.quantity
