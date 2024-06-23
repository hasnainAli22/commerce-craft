# products/serializers.py

from rest_framework import serializers
from products.models import Product, ProductCategory
from products.utils import extract_features_from_image, serialize_features

class ProductCategoryReadSerializer(serializers.ModelSerializer):
    """
    Serializer class for product categories
    """
    class Meta:
        model = ProductCategory
        fields = "__all__"

class ProductReadSerializer(serializers.ModelSerializer):
    """
    Serializer class for reading products
    """
    seller = serializers.CharField(source="seller.get_full_name", read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

class ProductWriteSerializer(serializers.ModelSerializer):
    """
    Serializer class for writing products
    """
    seller = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = ProductCategoryReadSerializer()

    class Meta:
        model = Product
        fields = (
            "seller",
            "category",
            "name",
            "desc",
            "image",
            "price",
            "quantity",
        )

    def create(self, validated_data):
        category_data = validated_data.pop("category")
        category, _ = ProductCategory.objects.get_or_create(**category_data)
        product = Product.objects.create(**validated_data, category=category)

        # Extract and save image features
        features = extract_features_from_image(product.image.path)
        product.serialize_features(features)
        product.save()
        
        return product

    def update(self, instance, validated_data):
        if "category" in validated_data:
            nested_serializer = self.fields["category"]
            nested_instance = instance.category
            nested_data = validated_data.pop("category")
            nested_serializer.update(nested_instance, nested_data)

        instance = super(ProductWriteSerializer, self).update(instance, validated_data)

        # Extract and save image features if the image has changed
        if "image" in validated_data:
            features = extract_features_from_image(instance.image.path)
            instance.serialize_features(features)
            instance.save()
            
        return instance
    

class ImageSearchSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("No image uploaded.")
        return value