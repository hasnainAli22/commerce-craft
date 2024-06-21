# products/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from products.views import ProductCategoryViewSet, ProductViewSet, search_by_image

app_name = "products"

router = DefaultRouter()
router.register(r"categories", ProductCategoryViewSet)
router.register(r"", ProductViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("search_by_image/", search_by_image, name="search_by_image"),
]
