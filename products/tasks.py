# core/tasks.py

from celery import shared_task
from core.celery import app
from celery.utils.log import get_task_logger
from PIL import Image
import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models import ResNet50_Weights
from products.models import Product
import os

logger = get_task_logger(__name__)

# Load the pre-trained ResNet50 model
model = models.resnet50(weights=ResNet50_Weights.DEFAULT)
model = nn.Sequential(*list(model.children())[:-1])
model.eval()

def load_image(image_path):
    try:
        logger.info(f"Opening image: {image_path}")
        image = Image.open(image_path).convert('RGB')
        logger.info(f"Image opened successfully: {image_path}")
        return image
    except Exception as e:
        logger.error(f"Error opening image: {e}")
        raise

def preprocess_image(image):
    try:
        logger.info(f"Image size before resize: {image.size}")
        
        # Resize
        image = image.resize((256, 256))
        logger.info(f"Image size after resize: {image.size}")
        
        # Center crop
        width, height = image.size
        new_width, new_height = 224, 224
        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2
        image = image.crop((left, top, right, bottom))
        logger.info(f"Image size after center crop: {image.size}")
        
        # Convert to numpy array
        image_np = np.array(image).astype(np.float32)
        logger.info(f"Numpy array shape: {image_np.shape}")

        # Normalize
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image_np = (image_np / 255.0 - mean) / std
        logger.info("Normalization completed.")
        
        # Convert to tensor
        logger.info("Converting to tensor")
        image_tensor = torch.tensor(image_np).permute(2, 0, 1).unsqueeze(0)
        logger.info(f"Image tensor shape: {image_tensor.shape}")

        return image_tensor
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise

def extract_features(image_tensor):
    try:
        with torch.no_grad():
            features = model(image_tensor)
        features = features.squeeze().numpy()
        logger.info("Extracted features successfully")
        return features
    except Exception as e:
        logger.error(f"Error extracting features: {e}")
        raise

@app.task
def extract_and_save_features(product_id):
    try:
        logger.info(f"Started task for product ID: {product_id}")
        product = Product.objects.first()
        logger.info(f"Product Image Path: {product.image.path}")

        if not os.path.exists(product.image.path):
            logger.error(f"File does not exist: {product.image.path}")
            return

        logger.info("File exists, proceeding with feature extraction")

        image = load_image(product.image.path)
        image_tensor = preprocess_image(image)

        logger.info(f"Image tensor shape: {image_tensor.shape}")

        features = extract_features(image_tensor)

        logger.info(f"Extracted features: {features}")

        product.serialize_features(features)
        product.save()

        logger.info('Task completed successfully')
        return product.id
    except Product.DoesNotExist:
        logger.error(f"Product with ID {product_id} does not exist.")
    except Exception as e:
        logger.error(f"Error in task extract_and_save_features: {e}")
        raise
@app.task
def add_the_numbers(a,b,c):
    return 5