from django.contrib import admin
from .models import Customer, Product, License


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('key', 'customer', 'product', 'expires_at')
    list_filter = ('product', 'expires_at')
    search_fields = ('key', 'customer__name', 'product__name')
