from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    final_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "discount_price",
            "final_price",
            "stock",
            "is_active",
            "image",
            "category",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at", "final_price"]
