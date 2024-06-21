# products/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
from products.tasks import extract_and_save_features, add_the_numbers

@receiver(post_save, sender=Product)
def trigger_feature_extraction(sender, instance, created, **kwargs):
    if created:
        add_the_numbers.delay(10, 20, instance.id)
        print('new product is created')
        # extract_and_save_features.delay(instance.id)
