from django.db.models import F
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Category, Product, StockMovement, Supplier
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    StockMovementSerializer,
    SupplierSerializer,
)
from .services import InsufficientStockError, InvalidQuantityError, register_movement


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related("category", "supplier")
        if self.request.query_params.get("low_stock") == "1":
            queryset = queryset.filter(quantity__lte=F("minimum_stock"))
        return queryset

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        products = Product.objects.filter(quantity__lte=F("minimum_stock"))
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class StockMovementViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Movimentações são apenas criadas e consultadas, nunca editadas.

    Isso mantém o histórico de estoque confiável.
    """

    queryset = StockMovement.objects.select_related("product")
    serializer_class = StockMovementSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            movement = register_movement(
                product_id=data["product"].pk,
                kind=data["kind"],
                quantity=data["quantity"],
                note=data.get("note", ""),
            )
        except InsufficientStockError as exc:
            raise ValidationError({"quantity": str(exc)})
        except InvalidQuantityError as exc:
            raise ValidationError({"quantity": str(exc)})

        output = self.get_serializer(movement)
        return Response(output.data, status=status.HTTP_201_CREATED)
