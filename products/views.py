from django.shortcuts import render
from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view


# Create your views here.
@extend_schema_view(
    # Configuration for Listing (GET)
    get=extend_schema(
        tags=['Products'],
        summary="List active products",
        description="Returns a list of all products where is_active=True, ordered by creation date."
    ),
    # Configuration for Creating (POST)
    post=extend_schema(
        tags=['Products'],
        summary="Create a new product",
        description="Create a new product entry. Requires admin permissions."
    ),
)
class ProductListView(generics.ListCreateAPIView):
    """
        GET  /products/  => List only active products
        POST /products/  => Create a product
    """
    # queryset = Product.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ProductSerializer


    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by('-created_at')


@extend_schema_view(
    # Configuration for Retrieving (GET)
    get=extend_schema(
        tags=['Products'],
        summary="Retrieve single product",
        description="Get detailed information about a specific product by ID."
    )
)
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

