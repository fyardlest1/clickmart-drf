# orders/views.py
"""
Architecture Pattern Used
Thin View → Service Layer → Atomic Transaction

APIView
 └── PlaceOrderService
     ├── Validate cart
     ├── Create order
     ├── Create order items
     ├── Calculate totals
     └── Lock order
"""
import datetime
import logging

from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.core.mail import BadHeaderError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView

from orders.models import Order, OrderItem
from carts.models import Cart
from products.models import Product
from .serializers import OrderSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

from .utils import send_order_confirmation_email, send_order_notification_simple_email


logger = logging.getLogger(__name__)

# Idempotency Helper to Generate order number
def generate_order_number():
    return f"ORD-{get_random_string(10).upper()}"


class PlaceOrderView(APIView):
    """
    Enterprise-grade checkout endpoint.
    Converts a cart into a pending order.
    """

    # user must be logged in to place order
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Orders'],
        summary="Place an order",
        description="Convert the current user's cart into an order."
    )
    def post(self, request):
        user = request.user
        # cart = Cart.objects.get(user=user)

        try:
            # get the cart
            cart = Cart.objects.select_related("user").prefetch_related(
                "items__product"
            ).get(user=user)
            # print(f'Cart ==> {cart}')
            # print(f'Cart Itemd ==> {cart.items.count()}')
        except Cart.DoesNotExist:
            return Response(
                {"detail": "No active cart found."},
                status=status.HTTP_400_BAD_REQUEST
            )        

        # check if the cart is empty
        if not cart.items.exists():
            return Response(
                {"detail": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # ───────────────────────────────
        # Validate Addresses
        # ───────────────────────────────
        shipping_address_front = request.data.get("shippingAddress") # shippingAddress is coming from frontend
        
        # billing_address = request.data.get("billingAddress")
                
        # if not shipping_address or not billing_address:
        #     return Response(
        #         {"detail": "Shipping and billing address are required."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
            
        if not shipping_address_front:
            return Response(
                {"detail": "Shipping and billing address are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            

        # creation of the order
        with transaction.atomic():
            # ───────────────────────────────
            # Create Order instence
            # ───────────────────────────────
            order = Order.objects.create(
                user=user,
                order_number=generate_order_number(),
                status='PENDING',
                phone=shipping_address_front.get("phone"),
                shipping_address=shipping_address_front.get("address"),
                city=shipping_address_front.get("city"),
                state=shipping_address_front.get("state"),
                postal_code=shipping_address_front.get("zipCode"),
                country=shipping_address_front.get("country"),
                # currency=Order.currency,
                # billing_address = billing_address,
                # shipping_amount = cart.shipping_cost
                # discount_amount = cart.discount_amount
            )

            # ───────────────────────────────
            # Create Order Items (Snapshots)
            # ───────────────────────────────
            order_items = []

            # for cart_item in cart.items.all():
            #     product = cart_item.product
            for cart_item in cart.items.select_related("product"):
                # 🔒 Lock the product row until transaction finishes
                product = (
                    Product.objects
                    .select_for_update()
                    .get(pk=cart_item.product_id)
                )
                
                # Optional: check if enough stock exists
                # Stock validation
                if product.stock < cart_item.quantity:
                    raise ValidationError(
                        f"Insufficient stock for '{product.name}'. "
                        f"Available: {product.stock}, "
                        f"Requested: {cart_item.quantity}"
                    )
                
                # Decrease product stock using F() to avoid race conditions
                # avoids issues if multiple orders are processed simultaneously
                product.stock = F('stock') - cart_item.quantity
                product.save(update_fields=['stock'])

                # Create the order item snapshot
                item = OrderItem(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_description=product.description or "",
                    unit_price=product.final_price,
                    quantity=cart_item.quantity,
                    tax_percent=product.tax_percent,
                )

                item.calculate_totals()
                order_items.append(item)

            OrderItem.objects.bulk_create(order_items)

            # ───────────────────────────────
            # Final Totals / Freeze Totals
            # ───────────────────────────────
            order.recalculate_from_items()
            order.save(
                update_fields=["subtotal", "tax_amount", "total_amount"]
            )

            # ───────────────────────────────────────
            # Clear Cart (NOT deactivate) / Lock Cart
            # ───────────────────────────────────────
            cart.items.all().delete()
        
        # ───────────────────────────────
        # Send Notification Email to Customer (outside transaction / atomic block)
        # ───────────────────────────────
        # We want Order creation to never fail because of email
        # Correct Way to Call It (Production-Grade)
        try:
            # send_order_notification_simple_email(order)
            send_order_confirmation_email(order)
        except BadHeaderError:
            logger.exception(
                f"Invalid email header found when sending order confirmation for order {order.order_number}",
                extra={"order_id": str(order.id)}
            )
        except Exception as e:
            logger.exception(
                f"Error sending order confirmation for order {order.order_number}, see details below.",
                extra={"order_id": str(order.id), "error": str(e)}
            )
            
        # ───────────────────────────────
        # Response
        # ───────────────────────────────
        serializer = OrderSerializer(order)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # return Response(
        #     {
        #         "order_id": order.id,
        #         "order_number": order.order_number,
        #         "status": order.status,
        #         "total_amount": order.total_amount,
        #         "currency": order.currency,
        #     },
        #     status=status.HTTP_201_CREATED
        # )


@extend_schema_view(
    get=extend_schema(
        tags=['Orders'],
        summary="List customer orders",
        description="Retrieve a list of orders placed by the currently logged-in user."
    )
)
class CustomerOrderView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        # Fetch all orders for this user, and preload their related order items efficiently.
        # "items" is the reverse relation from Order → OrderItem
        return Order.objects.filter(user=user).prefetch_related("items")


@extend_schema_view(
    get=extend_schema(
        tags=['Orders'],
        summary="Get order details",
        description="Retrieve the details of a specific order by its ID for the current user."
    )
)
class OrderDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    lookup_field = "id"
    
    def get_object(self):
        user = self.request.user
        order_id = self.kwargs.get("id")
        order = get_object_or_404(
            Order.objects.prefetch_related("items"),
            user=user,
            id=order_id
        )
        return order
    
    # def get_queryset(self):
    #     user = self.request.user
    #     return Order.objects.filter(user=user).prefetch_related("items")
