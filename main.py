from ultralytics import YOLO, settings

settings.reset()
# Load model
model = YOLO('yolov8x-seg.pt')

yolo_yaml = 'data/YOLO/HL_data.yaml'

# Transfer learning
results = model.train(
    data=yolo_yaml,
    imgsz=640,
    epochs=100,
    batch=8,
    name='ybest.pt'
)
