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

from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView

from orders.models import Order, OrderItem
from carts.models import Cart
from .serializers import OrderSerializer

from .utils import send_order_confirmation_email, send_order_notification_simple_email
from django.core.mail import BadHeaderError
import logging

logger = logging.getLogger(__name__)

# Idempotency Helper to Generate order number
def generate_order_number():
    return f"ORD-{get_random_string(10).upper()}"

# Idempotency Helper to Generate current date for order number
# def order_number_current_date():
#     yr = int(datetime.date.today().strftime('%Y'))
#     dt = int(datetime.date.today().strftime('%d'))
#     mt = int(datetime.date.today().strftime('%m'))
#     d = datetime.date(yr,mt,dt)
#     current_date = d.strftime("%Y%m%d") #20210305
#     # order_number = current_date + str(data.id)
#     return current_date


class PlaceOrderView(APIView):
    """
    Enterprise-grade checkout endpoint.
    Converts a cart into a pending order.
    """

    # user must be logged in to place order
    permission_classes = [IsAuthenticated]

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
        shipping_address = request.data.get("shippingAddress")
        
        # billing_address = request.data.get("billingAddress")
                
        # if not shipping_address or not billing_address:
        #     return Response(
        #         {"detail": "Shipping and billing address are required."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
            
        if not shipping_address:
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
                status=Order.Status.PENDING,
                shipping_address=shipping_address,
                phone=shipping_address.get("phone"),
                city=shipping_address.get("city"),
                postal_code=shipping_address.get("zipCode"),
                # currency=Order.currency,
                # billing_address = billing_address,
                # country=shipping_address.get("country"),
                # shipping_amount = cart.shipping_cost
                # discount_amount = cart.discount_amount
            )

            # ───────────────────────────────
            # Create Order Items (Snapshots)
            # ───────────────────────────────
            order_items = []

            for cart_item in cart.items.all():
                product = cart_item.product

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


class CustomerOrderView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Fetch all orders for this user, and preload their related order items efficiently.
        # "items" is the reverse relation from Order → OrderItem
        return Order.objects.filter(user=user).prefetch_related("items")


class OrderDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    lookup_field = "id"
    
    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).prefetch_related("items")
