import os
from ultralytics.data.annotator import auto_annotate

un_annotated_images_dir = 'data/tank_video_frames'

# Auto annotate the images with pre-trained model
for folder in os.listdir(un_annotated_images_dir):
    if folder == '.gitkeep':
        continue
    auto_annotate(data=f'{un_annotated_images_dir}/{folder}', det_model='ybest.pt', sam_model='mobile_sam.pt', output_dir=f'data/auto_annotated/{folder}')

for folder in os.listdir('data/auto_annotated'):
    for image in os.listdir(f'data/auto_annotated/{folder}'):
        os.rename(f'data/auto_annotated/{folder}/{image}', f'data/auto_annotated/{folder}_{image[:-4]}.txt')
    os.rmdir(f'data/auto_annotated/{folder}')

