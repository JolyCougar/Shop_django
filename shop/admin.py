from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Product, ProductImage, Order, Category, Manufacturer


class ProductImageInline(admin.StackedInline):
    model = ProductImage


@admin.action(description='Archive products')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description='Unarchive products')
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [
        mark_archived,
        mark_unarchived,
    ]
    inlines = [
        ProductImageInline
    ]
    list_display = "pk", "name", 'category', "description_short", 'stock', "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "name", "pk"
    search_fields = "name", "description"
    fieldsets = [
        (None, {
            "fields": ("name", "description",
                       "category", "manufacturer",
                       "stock"),
            "classes": ("wide", "collapse"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse"),
        }),
        ("Images", {
            "fields": ("preview",),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = "delivery_address", "promo", "order_date", 'total_price', "user", 'status'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = "name",


@admin.register(Manufacturer)
class Manufacturer(admin.ModelAdmin):
    list_display = "name",