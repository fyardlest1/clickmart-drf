from django.contrib import admin
from .models import Cart, CartItem


admin.site.register(Cart)
admin.site.register(CartItem)
# view and edit all items inside a cart directly from the cart admin page
# class CartItemInline(admin.TabularInline):
#     """
#     Shows CartItems inline inside a Cart admin page.
#     """
#     model = CartItem
#     extra = 0
#     readonly_fields = ("subtotal",) # Prevent accidental changes; it’s calculated automatically.
#     autocomplete_fields = ("product",)


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     """
#     Cart admin view with inline cart items.
#     """
#     list_display = ("user", "total", "created_at")
#     search_fields = ("user__username", "user__email")
#     inlines = [CartItemInline]
#     readonly_fields = ("total",)

#     def total(self, obj):
#         return obj.total
#     total.short_description = "Cart Total"


# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     """
#     Optional: Manage CartItems individually if needed.
#     """
#     list_display = ("cart", "product", "quantity", "subtotal")
#     list_filter = ("cart",)
#     search_fields = ("product__name",)
#     readonly_fields = ("subtotal",)
#     autocomplete_fields = ("product", "cart")
