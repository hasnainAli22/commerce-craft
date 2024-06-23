# products/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
from products.utils import extract_features_from_image

@receiver(post_save, sender=Product)
def trigger_feature_extraction(sender, instance, created, **kwargs):
    if created:
        # When product is created get extract the features from the image and save in feature filed
        product = Product.objects.get(id=instance.id)
        features = extract_features_from_image(product.image.path)
        product.serialize_features(features)
        product.save()
