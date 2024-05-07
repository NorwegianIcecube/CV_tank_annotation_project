import os
from ultralytics.data.annotator import auto_annotate

un_annotated_images_dir = 'data/tank_video_frames'
export_dir = 'data/auto_annotated'

# Auto annotate the images with pre-trained model
auto_annotate(data=f'{un_annotated_images_dir}', det_model='ybest.pt', sam_model='mobile_sam.pt', output_dir=f'{export_dir}')