# products/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
from products.tasks import extract_and_save_features, add_the_numbers
from products.utils import extract_features_from_image

@receiver(post_save, sender=Product)
def trigger_feature_extraction(sender, instance, created, **kwargs):
    if created:
        print('New product is created')
        product = Product.objects.get(id=instance.id)
        print("New product name is :>", product.name)

        # Assuming extract_features_from_image is defined elsewhere
        features = extract_features_from_image(product.image.path)
        print("Feature extraction completed")

        product.serialize_features(features)
        print('Product serialization completed')

        product.save()
        print("Product save complete")
