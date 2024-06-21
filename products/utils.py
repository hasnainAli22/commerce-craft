# products/utils.py

import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models import ResNet50_Weights
import torchvision.transforms as transforms
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import base64

from .models import Product

# Load the pre-trained ResNet50 model
model = models.resnet50(weights=ResNet50_Weights.DEFAULT)
model = nn.Sequential(*list(model.children())[:-1])
model.eval()

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def load_and_preprocess_image(image_path):
    image = Image.open(image_path).convert('RGB')
    image = preprocess(image)
    image = image.unsqueeze(0)
    return image

def extract_features(image_tensor):
    with torch.no_grad():
        features = model(image_tensor)
    features = features.squeeze().numpy()
    return features

def extract_features_from_image(image_path):
    image_tensor = load_and_preprocess_image(image_path)
    return extract_features(image_tensor)

def serialize_features(features):
    return base64.b64encode(features.tobytes()).decode('utf-8')

def deserialize_features(features_str):
    return np.frombuffer(base64.b64decode(features_str), dtype=np.float32)

def calculate_similarity(feature1, feature2):
    feature1 = feature1.reshape(1, -1)
    feature2 = feature2.reshape(1, -1)
    similarity = cosine_similarity(feature1, feature2)[0][0]
    return similarity

def find_similar_products(uploaded_image_path):
    uploaded_features = extract_features_from_image(uploaded_image_path)
    products = Product.objects.all()
    similarities = []

    for product in products:
        product_features = product.deserialize_features()
        similarity = calculate_similarity(uploaded_features, product_features)
        similarities.append((product, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    similar_products = [product for product, _ in similarities]

    return similar_products
