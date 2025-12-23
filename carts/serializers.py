# cart/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import get_object_or_404
from products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    # Additional read-only field to expose product name directly
    product_name = serializers.CharField(source="product.name", read_only=True)
    
    price = serializers.DecimalField(
        source="product.final_price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    tax_percent = serializers.DecimalField(
        source="product.tax_percent",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        read_only=True
    )

    subtotal = serializers.SerializerMethodField()
    
    # Field used only when adding an item to the cart
    # The client sends product_id, but it is not returned in responses
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CartItem

        # Fields exposed by the API
        fields = [
            "id",
            "product_id",
            "product_name",
            "price",
            "tax_percent",
            "quantity",
            "subtotal",
        ]

        # Fields that cannot be modified by the client
        read_only_fields = ["id", "subtotal"]

    # MUST be here (same level as Meta)
    def get_subtotal(self, obj):
        # Use the model property, but ensure rounding
        return Decimal(obj.subtotal).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Custom create method to handle adding items to cart
    def create(self, validated_data):
        # Remove product_id from validated_data
        # because CartItem model expects a Product instance, not an ID
        product_id = validated_data.pop("product_id")
        quantity = validated_data.get("quantity", 1)

        # Retrieve the user's cart from the serializer context
        # (passed from the view)
        cart = self.context["cart"]

        # Fetch the product using the provided product_id
        # Only active products can be added to the cart
        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )

        # Try to find an existing CartItem for this cart and product
        # If it doesn't exist, create it with a default quantity
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity}
        )

        # If the item already exists in the cart
        # increase the quantity instead of creating a duplicate row
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        # Return the CartItem instance (new or updated)
        return item


class CartSerializer(serializers.ModelSerializer):
    # nested serializer for cart items
    items = CartItemSerializer(many=True, read_only=True)
    
    # Computed pricing fields
    # subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    # tax_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    # total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()
    tax_total = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        # This serializer is linked to the Cart model
        model = Cart
        fields = ["id", "user", "items", "subtotal", "tax_total", "total"]
        read_only_fields = fields
    
    def get_subtotal(self, obj):
        return round(obj.subtotal, 2)

    def get_tax_total(self, obj):
        return round(obj.tax_total, 2)

    def get_total(self, obj):
        return round(obj.total, 2)
    
    # Override to_representation to sort items by their ID
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data["items"] = sorted(
    #         data["items"],
    #         key=lambda item: item["id"]
    #     )
    #     return data

