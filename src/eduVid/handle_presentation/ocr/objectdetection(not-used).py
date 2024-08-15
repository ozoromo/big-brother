import torch
from pathlib import Path
from PIL import Image
import os

##pip install torch torchvision
##git clone https://github.com/ultralytics/yolov5
##cd yolov5
##pip install -U -r requirements.txt


# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # Load pre-trained YOLOv5 model

def detect_objects(image_path):
    # Load and preprocess the image
    img = Image.open(image_path)

    # Perform object detection
    results = model(img)

    # Process results
    detections = results.xyxy[0].cpu().numpy()  # Get bounding boxes and class labels

    # Check if any objects are detected with a confidence above a threshold (e.g., 0.5)
    if detections.shape[0] > 0.5:
        return True
    return False



# Directory containing slide images
slides_directory = 'path/to/slides_directory'  # CHANGE THIS TO YOUR DIRECTORY


# Check each image in the directory
for filename in os.listdir(slides_directory):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        image_path = os.path.join(slides_directory, filename)
        try:
            has_objects = detect_objects(image_path)     ##CUSTOM NOT IMPORTANT OBJECTS??? , LIKE LOGO????
            print(f"{filename} has objects: {has_objects}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")


def save_image(image_path, output_directory):
    # Save the image to a specified directory
    os.makedirs(output_directory, exist_ok=True)
    filename = os.path.basename(image_path)
    destination_path = os.path.join(output_directory, filename)
    shutil.copy(image_path, destination_path)
    print(f"Saved image with objects: {image_path} to {destination_path}")

# Directory containing slide images
slides_directory = 'path/to/slides_directory'  # CHANGE THIS TO YOUR DIRECTORY
output_directory_with_objects = 'path/to/output_directory_with_objects'  # CHANGE THIS TO YOUR DIRECTORY
processed_directory = 'path/to/processed_directory'  # Directory for processed images

# Lists to store paths
slides_with_objects = []
slides_without_objects = []

# Process each image                        //if it has object--> save , else send to ocr
for filename in os.listdir(slides_directory):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        image_path = os.path.join(slides_directory, filename)
        try:
            has_objects = detect_objects(image_path)
            if has_objects:
                slides_with_objects.append(image_path)
                save_image(image_path, output_directory_with_objects)
            else:
                slides_without_objects.append(image_path)
                apply_custom_processing(image_path)   ##--> here comes the ocr function: NEXT STEP SET UP AND IMPLEMENT GOOGLE OCR.S
        except Exception as e:
            print(f"Error processing {filename}: {e}")           