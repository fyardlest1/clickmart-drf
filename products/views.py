from django.shortcuts import render
from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

# Create your views here.
class ProductListView(generics.ListCreateAPIView):
    """
        GET  /products/  => List only active products
        POST /products/  => Create a product
    """
    # queryset = Product.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ProductSerializer
        
    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by('-created_at')


class ProductDetailView(generics.RetrieveAPIView):
    """GET    /products/<id>/  => Retrieve single product"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = "id"


# class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     GET    /products/<id>/  => Retrieve single product
#     PUT    /products/<id>/  => Full update
#     PATCH  /products/<id>/  => Partial update
#     DELETE /products/<id>/  => Delete
#     """
#     queryset = Product.objects.filter(is_active=True)
#     serializer_class = ProductSerializer
#     lookup_field = "id"
    

















# Example POST Body
# {
#   "name": "Mango Smoothie",
#   "description": "Fresh tropical mango blend",
#   "price": "9.99",
#   "discount_price": "7.99",
#   "stock": 20,
#   "category": "Drinks"
# }

