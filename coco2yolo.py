from JSON2YOLO.general_json2yolo import convert_coco_json

coco_dir = 'data/COCO/'

convert_coco_json(json_dir=coco_dir, use_segments=True, cls91to80=False)