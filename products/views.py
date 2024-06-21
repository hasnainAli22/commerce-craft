# products/views.py

from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.files.storage import default_storage
from products.models import Product, ProductCategory
from products.permissions import IsSellerOrAdmin
from products.serializers import ProductCategoryReadSerializer, ProductReadSerializer, ProductWriteSerializer
from products.utils import find_similar_products

class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and Retrieve product categories
    """
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategoryReadSerializer
    permission_classes = (permissions.AllowAny,)

class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD products
    """
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return ProductWriteSerializer
        return ProductReadSerializer

    def get_permissions(self):
        if self.action in ("create",):
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = (IsSellerOrAdmin,)
        else:
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissions()

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def search_by_image(request):
    if 'image' not in request.FILES:
        return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['image']
    image_path = default_storage.save('uploads/' + uploaded_file.name, uploaded_file)
    full_image_path = default_storage.path(image_path)

    similar_products = find_similar_products(full_image_path)

    serializer = ProductReadSerializer(similar_products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
