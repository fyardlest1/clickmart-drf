import uuid
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

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

    @property
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

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.final_price * self.quantity
