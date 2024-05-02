from ultralytics import YOLO
import os

# Load model
model = YOLO('yolov8n-seg.pt')

yolo_yaml = 'data/YOLO/HL_data.yaml'

# Transfer learning
model.train(data=yolo_yaml, epochs=5)

# Save the model
model.save('yolov8n-seg-tanks.pt')

# Test the model
results = model.test(data=yolo_yaml)

# Print the results

print(results)


