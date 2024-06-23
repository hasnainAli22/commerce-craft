from django.urls import include, path
from rest_framework.routers import DefaultRouter
from products.views import ProductCategoryViewSet, ProductViewSet, ImageSearchView

app_name = "products"

router = DefaultRouter()
router.register(r"categories", ProductCategoryViewSet)
router.register(r"products", ProductViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("search_with_image/", ImageSearchView.as_view(), name="search_with_image_view"),
]
