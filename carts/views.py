from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema


# THE FOLLOWING CODE USE APIVIEW INSTEAD OF GENERICS

# Helper function to get or create a cart
# Get the cart for user or create one if it doesn't exist
def get_or_create_cart(user):
    # print(f'Cart => {cart}')
    # print(f'Created => {created}')
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    """
    GET /cart/ => Get current user's cart
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cart'],
        summary="Get cart details",
        description="Retrieve the details of the currently logged-in user's cart."
    )
    def get(self, request):
        # get or create the cart
        cart = get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cart'],
        summary="Add product to cart",
        description="Add a specified product to the current user's cart."
    )
    def post(self, request):
        # take the input
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity') # 2

        if not product_id:
            return Response({'error': 'product_id is required'})
        
        # get the product
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # get or create the cart
        cart = get_or_create_cart(request.user)

        # get or create cartitem
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created: # cart item already exist
            # item.quantity = item.quantity + quantity
            item.quantity += int(quantity)
            item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ManageCartItemView(APIView):
    """
    PATCH /cart/items/<item_id>/ => Update cart item quantity
    Body:
    {
        "quantity": 5
    }
    """
    @extend_schema(
        tags=['Cart'],
        summary="Update cart item",
        description="Update the quantity of a specific item in the cart."
    )
    def patch(self, request, item_id):
        # validate
        if 'change' not in request.data:
            return Response({'error': "Provide 'change' ield"})
        
        change = int(request.data.get('change')) # +1 or -1
        
        item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        product = item.product
        
        # for adding, check the stock
        if change > 0: # -> chage = 1
            if item.quantity + change > product.stock:
                return Response({'error': 'Not enough stock'})
            
        # change can be +1 or -1 (delta)
        # -> new_qty = 2 + (+1) -> or -> new_qty = 2 + (-1)
        new_qty = item.quantity + change
        
        if new_qty <= 0:
            # remove item from cart
            item.delete()
            return Response({'success': 'item remove'})
        
        # update the new quantity
        item.quantity = new_qty
        item.save()
        serializer = CartItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(tags=["Cart"], summary="Remove cart item", description="Remove a specific item from the cart.")
    def delete(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
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
'''


# class CartItemDetailView(APIView):
#     """
#     PATCH /cart/items/<item_id>/ => Update cart item quantity
#     DELETE /cart/items/<item_id>/ => Remove product from cart
#     """
#     permission_classes = [IsAuthenticated]

#     def get_object(self, item_id):
#         return get_object_or_404(CartItem, id=item_id)

#     @extend_schema(tags=["Cart"], summary="Update cart item quantity")
#     def patch(self, request, item_id):
#         cart_item = self.get_object(item_id)
#         serializer = CartItemSerializer(
#             cart_item, data=request.data, partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     @extend_schema(tags=["Cart"], summary="Remove cart item", description="Remove a specific item from the cart.")
#     def delete(self, request, item_id):
#         cart_item = self.get_object(item_id)
#         cart_item.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



