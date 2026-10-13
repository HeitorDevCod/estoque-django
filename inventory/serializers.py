from rest_framework import serializers

from .models import Category, Product, StockMovement, Supplier


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["id", "name", "email", "phone"]


class ProductSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "category",
            "supplier",
            "unit_price",
            "quantity",
            "minimum_stock",
            "is_low_stock",
        ]
        # A quantidade só muda por meio de movimentações, nunca direto.
        read_only_fields = ["quantity"]


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ["id", "product", "kind", "quantity", "note", "created_at"]
        read_only_fields = ["created_at"]
