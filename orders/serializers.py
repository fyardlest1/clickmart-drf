from rest_framework import serializers
from .models import Order, OrderItem, Refund


class OrderItemSerializer(serializers.ModelSerializer):    
    class Meta:
        model = OrderItem
        fields = "__all__"
        
        read_only_fields = [
            "id",
            "order",
            "product",
            "product_name",
            "product_sku",
            "product_description",
            "unit_price",
            "quantity",
            "tax_percent",
            "tax_amount",
            "discount_amount",
            "line_total",
            "created_at",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        
        read_only_fields = [
            "id",
            "order_number",
            "user",
            "status",
            "currency",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "shipping_amount",
            "total_amount",
            "payment_provider",
            "payment_reference",
            "paid_at",
            "created_at",
            "updated_at",
        ]


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = "__all__"
        read_only_fields = ["status", "provider_reference", "processed_at"]



