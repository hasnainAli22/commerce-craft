from django.urls import include, path
from rest_framework.routers import DefaultRouter
from products.views import ProductCategoryViewSet, ProductViewSet, ImageSearchView, try_me, search_by_image

app_name = "products"

router = DefaultRouter()
router.register(r"categories", ProductCategoryViewSet)
router.register(r"products", ProductViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("search_by_image/", search_by_image, name="search_by_image"),
    path("search_with_image/", ImageSearchView.as_view(), name="search_with_image_view"),
    path('testing/', try_me, name="testing"),
]
