import logging
from PIL import Image
import torchvision.transforms as transforms
import torch
from torch import nn
import torchvision.models as models
from torchvision.models import ResNet50_Weights

logging.basicConfig(level=logging.INFO)

# Load the pre-trained ResNet50 model
model = models.resnet50(weights=ResNet50_Weights.DEFAULT)
model = nn.Sequential(*list(model.children())[:-1])
model.eval()

preprocess_resize = transforms.Resize(256)
preprocess_center_crop = transforms.CenterCrop(224)
preprocess_to_tensor = transforms.ToTensor()
preprocess_normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

def load_image(image_path):
    try:
        logging.info(f"Opening image: {image_path}")
        image = Image.open(image_path).convert('RGB')
        logging.info(f"Image opened successfully: {image_path}")
        return image
    except Exception as e:
        logging.error(f"Error opening image: {e}")
        raise

def preprocess_image(image):
    try:
        logging.info(f"Image size before resize: {image.size}")
        logging.info("Starting resize...")
        image = preprocess_resize(image)
        logging.info(f"Image size after resize: {image.size}")
        logging.info("Resize completed.")
        
        logging.info("Starting center crop...")
        image = preprocess_center_crop(image)
        logging.info(f"Image size after center crop: {image.size}")
        logging.info("Center crop completed.")
        
        logging.info("Starting to tensor...")
        image_tensor = preprocess_to_tensor(image)
        logging.info(f"Image tensor shape: {image_tensor.shape}")
        logging.info("To tensor completed.")
        
        logging.info("Starting normalization...")
        image_tensor = preprocess_normalize(image_tensor)
        logging.info("Normalization completed.")

        image_tensor = image_tensor.unsqueeze(0)
        logging.info(f"Final image tensor shape: {image_tensor.shape}")
        return image_tensor
    except Exception as e:
        logging.error(f"Error preprocessing image: {e}")
        raise

def extract_features(image_tensor):
    try:
        with torch.no_grad():
            features = model(image_tensor)
        features = features.squeeze().numpy()
        logging.info("Extracted features successfully")
        return features
    except Exception as e:
        logging.error(f"Error extracting features: {e}")
        raise

# Example usage
image_path = "smartwatch.jpg"
image = load_image(image_path)
image_tensor = preprocess_image(image)
features = extract_features(image_tensor)
print("Features:", features)
