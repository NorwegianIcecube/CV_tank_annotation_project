import os
import random

image_path = 'data/YOLO/images'
label_path = 'data/YOLO/labels'

# File strucutre should be:
# data
#   - YOLO
#       - images
#           - train
#           - val
#       - labels
#           - train
#           - val

# Get the images
images = os.listdir(image_path)

# Get the labels
labels = os.listdir(label_path)

# Create the directories
try:
    os.mkdir(f'{image_path}/train')
    os.mkdir(f'{image_path}/val')
    os.mkdir(f'{label_path}/train')
    os.mkdir(f'{label_path}/val')
except FileExistsError:
    pass

# Shuffle the images
random.shuffle(images)

# Split the images
train_images = images[:int(len(images)*0.8)]
val_images = images[int(len(images)*0.8):]

# Move the images
for image in train_images:
    print(image_path, image)
    os.rename(f'{image_path}/{image}', f'{image_path}/train/{image}')
    os.rename(f'{label_path}/{image[:-4]}.txt', f'{label_path}/train/{image[:-4]}.txt')

for image in val_images:
    os.rename(f'{image_path}/{image}', f'{image_path}/val/{image}')
    os.rename(f'{label_path}/{image[:-4]}.txt', f'{label_path}/val/{image[:-4]}.txt')

# Move the labels
for image in images:
    os.rename(f'{label_path}/{image[:-4]}.txt', f'{label_path}/train/{image[:-4]}.txt')
    os.rename(f'{label_path}/{image[:-4]}.txt', f'{label_path}/val/{image[:-4]}.txt')

# Print the number of images in each directory
print(f'Number of training images: {len(os.listdir(f"{image_path}/train"))}')
print(f'Number of validation images: {len(os.listdir(f"{image_path}/val"))}')
print(f'Number of training labels: {len(os.listdir(f"{label_path}/train"))}')
print(f'Number of validation labels: {len(os.listdir(f"{label_path}/val"))}')

