from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User

from .admin_permissoes import PermissoesAdminMixin
from .models import Category, Product, StockMovement, Supplier

admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(Group)
class GroupAdmin(PermissoesAdminMixin, BaseGroupAdmin):
    pass


@admin.register(User)
class UserAdmin(PermissoesAdminMixin, BaseUserAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    search_fields = ["name", "email"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "category", "quantity", "minimum_stock", "unit_price"]
    list_filter = ["category", "supplier"]
    search_fields = ["sku", "name"]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["product", "kind", "quantity", "note", "created_at"]
    list_filter = ["kind"]
    search_fields = ["product__sku", "product__name", "note"]
    readonly_fields = ["created_at"]
