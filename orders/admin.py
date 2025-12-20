from django.contrib import admin
from .models import Order, OrderItem, Refund


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("order", "product", "product_name", "unit_price", "quantity", "line_total", "product_description", "tax_percent", "tax_amount", "discount_amount", "product_sku",)
    extra = 0
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "total_amount", "currency", "created_at",)
    list_filter = ("status", "currency")
    search_fields = ("order_number", "user__email")
    readonly_fields = (
        "id",
        "subtotal",
        "tax_amount",
        "total_amount",
        "payment_provider",
        "payment_reference",
        "paid_at",
        "created_at",
        "updated_at",
    )

    inlines = [OrderItemInline]

    actions = ["mark_as_cancelled"]

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status=Order.Status.CANCELLED)

    mark_as_cancelled.short_description = "Cancel selected orders"
    

admin.site.register(OrderItem)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ( "id", "order", "amount", "status", "payment_provider", "created_at",)
    list_filter = ("status",)
    readonly_fields = ("order", "amount", "payment_provider", "provider_reference", "created_at",)
