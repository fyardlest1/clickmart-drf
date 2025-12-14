# cart/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer
from django.shortcuts import get_object_or_404


class CartItemSerializer(serializers.ModelSerializer):
    # Nested serializer to return full product details in responses
    # read_only=True means clients cannot modify product data through this serializer
    product = ProductSerializer(read_only=True)

    # Field used only when adding an item to the cart
    # The client sends product_id, but it is not returned in responses
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CartItem

        # Fields exposed by the API
        fields = ["id", "product", "product_id", "quantity", "subtotal"]

        # Fields that cannot be modified by the client
        read_only_fields = ["id", "subtotal"]

    def create(self, validated_data):
        # Remove product_id from validated_data
        # because CartItem model expects a Product instance, not an ID
        product_id = validated_data.pop("product_id")

        # Retrieve the user's cart from the serializer context
        # (passed from the view)
        cart = self.context["cart"]

        # Fetch the product using the provided product_id
        # Only active products can be added to the cart
        product = self.context["product_model"].objects.get(
            id=product_id,
            is_active=True
        )

        # Try to find an existing CartItem for this cart and product
        # If it doesn't exist, create it with a default quantity
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": validated_data.get("quantity", 1)}
        )

        # If the item already exists in the cart
        # increase the quantity instead of creating a duplicate row
        if not created:
            item.quantity += validated_data.get("quantity", 1)
            item.save()

        # Return the CartItem instance (new or updated)
        return item


class CartSerializer(serializers.ModelSerializer):
    # nested serializer for cart items
    items = CartItemSerializer(many=True, read_only=True)
    
    # Computed pricing fields
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tax_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        # This serializer is linked to the Cart model
        model = Cart
        fields = ["id", "user", "items", "total", "subtotal", "tax_total", "total"] 
        read_only_fields = fields
        
    # subtotal = serializers.SerializerMethodField()
    # def get_subtotal(self, obj):
    #     subtotal = 0
    #     for item in obj.items.all():
    #         subtotal += item.product.price * item.quantity
    #     return subtotal
    
    # total = serializers.SerializerMethodField()
    # def get_total(self, obj):
    #     total = 0
    #     for item in obj.items.all():
    #         subtotal = item.product.price * item.quantity
    #         tax = subtotal * (item.product.tax_percent / 100)
    #         total += subtotal + tax
        
    #     return total 
