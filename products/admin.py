from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "final_price", "tax_percent", "stock", "is_active", "created_at")
    list_filter = ("is_active", "category")
    list_editable = ("tax_percent", "is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    
