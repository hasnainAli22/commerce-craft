from django.contrib import admin
from products.models import Product, ProductCategory

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'features']  # Add 'features' to the list display

admin.site.register(ProductCategory)
admin.site.register(Product, ProductAdmin)
