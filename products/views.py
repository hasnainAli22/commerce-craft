# products/views.py

from rest_framework import permissions, viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from products.models import Product, ProductCategory
from products.permissions import IsSellerOrAdmin
from products.serializers import ProductCategoryReadSerializer, ImageSearchSerializer, ProductReadSerializer, ProductWriteSerializer
from products.utils import find_similar_products
from django.shortcuts import render

from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from products.tasks import extract_and_save_features, add_the_numbers



# views.py

from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from .utils import extract_features_from_image, serialize_features
from PIL import Image
import torchvision.transforms as transforms
preprocess_resize = transforms.Resize(256)
preprocess_center_crop = transforms.CenterCrop(224)
preprocess_to_tensor = transforms.ToTensor()

@csrf_exempt
def try_me(request):
    context = {}
    if request.method == "POST":
        # product = Product.objects.first()
        # image_path = product.image.path
        # # Open the image
        # image = Image.open(image_path).convert('RGB')

        # print(f"Image size before resize: {image.size}")
        # print("Starting resize...")
        # image = preprocess_resize(image)
        # print(f"Image size after resize: {image.size}")
        # print("Resize completed.")
        
        # print("Starting center crop...")
        # image = preprocess_center_crop(image)
        # print(f"Image size after center crop: {image.size}")
        # print("Center crop completed.")
        
        # print("Starting to tensor...")
        # try:
        #     image_tensor = preprocess_to_tensor(image)
        # except Exception as e:
        #     print(f"Error in ToTensor step: {e}")
        #     raise
        # print(f"Image tensor shape: {image_tensor.shape}")
        # print("To tensor completed.")

        # print("Image orange", image)

        extract_and_save_features.delay(1)
        print('I am working')
        context = {'msg': 'Image Uploaded and Processed successfully'}

    return render(request, 'oranges.html', context)
@csrf_exempt
def mynewview(request):
    context = {}
    if request.method == "POST" and 'image' in request.FILES:

        image = request.FILES['image']
        
        # Save the uploaded image to a temporary location
        file_path = default_storage.save('tmp/' + image.name, ContentFile(image.read()))
        tmp_file = os.path.join(default_storage.location, file_path)
        
        # Process the image to extract features
        features = extract_features_from_image(tmp_file)
        print("Features",features)
        serialized_features = serialize_features(features)
        print("Serialized Features",serialized_features)
        
        # Delete the temporary image file
        default_storage.delete(file_path)
        
        context = {'msg': 'Image Uploaded and Processed successfully', 'features': serialized_features}

    return render(request, 'oranges.html', context)

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


class ImageSearchView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        return Response("oranges", status=status.HTTP_200_OK)
    def post(self, request, *args, **kwargs):
        print("Roaming Inside the post")
        serializer = ImageSearchSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            if isinstance(image, InMemoryUploadedFile):
                image_path = '/tmp/' + image.name
                with open(image_path, 'wb+') as f:
                    for chunk in image.chunks():
                        f.write(chunk)
                print("Print Image path", image_path)
                features = extract_features_from_image(image_path)
                print("features extraction done" ,features)
                print("similar products find start")

                similar_products = find_similar_products(features)
                print("similar products find end", similar_products)

                product_serializer = ProductReadSerializer(similar_products, many=True)
                return Response(product_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)