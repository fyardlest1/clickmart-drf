from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from django.shortcuts import get_object_or_404


# THE FOLLOWING CODE USE APIVIEW INSTEAD OF GENERICS

# Helper function to get or create a cart
def get_or_create_cart(user):
    # print(f'Cart => {cart}')
    # print(f'Created => {created}')
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


class CartDetailView(APIView):
    """
    GET /cart/ => Get current user's cart
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToCartView(APIView):
    """
    POST /cart/add/ => Add product to cart
    Body:
    {
        "product_id": "uuid",
        "quantity": 2
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = get_or_create_cart(request.user)
        serializer = CartItemSerializer(
            data=request.data,
            context={
                "cart": cart,
                "product_model": Product
            }
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateCartItemView(APIView):
    """
    PUT/PATCH /cart/item/<item_id>/ => Update cart item quantity
    Body:
    {
        "quantity": 5
    }
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, item_id):
        return get_object_or_404(CartItem, id=item_id)

    def put(self, request, item_id):
        cart_item = self.get_object(item_id)
        serializer = CartItemSerializer(cart_item, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, item_id):
        cart_item = self.get_object(item_id)
        serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveCartItemView(APIView):
    """
    DELETE /cart/item/<item_id>/ => Remove product from cart
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, item_id):
        return get_object_or_404(CartItem, id=item_id)

    def delete(self, request, item_id):
        cart_item = self.get_object(item_id)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





# THE FOLLOWING CODE USE GENERICS INSTEAD OF APIVIEW
'''
# Helper function to get or create a cart
# Get the cart for user or create one if it doesn't exist
def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    # print(f'Cart => {cart}')
    # print(f'Created => {created}')
    return cart


# API view to retrieve the current user's cart
class CartDetailView(generics.RetrieveAPIView):
    """
    GET /cart/ => Get current user cart
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    # Return the cart object for the current user
    def get_object(self):
        return get_or_create_cart(self.request.user)


# API view to add a product to the current user's cart
class AddToCartView(generics.CreateAPIView):
    """
    POST /cart/add/ => Add product to cart
    Body:
    {
        "product_id": "uuid",
        "quantity": 2
    }
    """
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    # Pass cart and product model context to the serializer
    def get_serializer_context(self):
        return {
            "cart": get_or_create_cart(self.request.user),
            "product_model": Product
        }


# API view to update quantity of a cart item
class UpdateCartItemView(generics.UpdateAPIView):
    """
    PUT/PATCH /cart/item/<item_id>/
    Body:
    {
        "quantity": 5
    }
    """
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "id"


# API view to remove a cart item
class RemoveCartItemView(generics.DestroyAPIView):
    """
    DELETE /cart/item/<item_id>/ → remove product from cart
    """
    queryset = CartItem.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
'''

