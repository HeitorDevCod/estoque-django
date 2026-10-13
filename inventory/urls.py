from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductViewSet,
    StockMovementViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("suppliers", SupplierViewSet)
router.register("products", ProductViewSet, basename="product")
router.register("movements", StockMovementViewSet, basename="movement")

urlpatterns = router.urls
