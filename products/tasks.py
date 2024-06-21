# products/tasks.py

from celery import shared_task
from products.models import Product
from products.utils import extract_features_from_image, serialize_features
import logging
import sys

@shared_task
def extract_and_save_features(product_id):
    print("THis is the product ID: ",product_id)
    
    product = Product.objects.get(id=product_id)
    features = extract_features_from_image(product.image.path)
    product.serialize_features(features)
    product.save()
    logging.info('Task is running...!')
    logging.info(f"Extracted features: {features}")
    print("Task is running")
    print("features", features)
    sys.stdout.flush()  # Flush output

@shared_task
def add_the_numbers(x,y,id):
    print("This is the instance id", id)
    add_numbers = x + y
    print(add_numbers)
    return id
