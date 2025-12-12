# cart/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "subtotal"]
        read_only_fields = ["id", "subtotal"]

    def create(self, validated_data):
        product_id = validated_data.pop("product_id")
        cart = self.context["cart"]
        product = self.context["product_model"].objects.get(id=product_id, is_active=True)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={"quantity": validated_data.get("quantity", 1)}
        )

        if not created:
            item.quantity += validated_data.get("quantity", 1)
            item.save()

        return item


class CartSerializer(serializers.ModelSerializer):    
    items = CartItemSerializer(many=True, read_only=True) # nested serializer
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total"]
        read_only_fields = ["id", "user", "total"]
