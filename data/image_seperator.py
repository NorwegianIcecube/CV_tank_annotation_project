import cv2
import os

video_path = './data/tank_videos'

image_path = './data/tank_video_frames'

FRAMES_PER_IMAGE = 50

def get_frames(video, frame_interval):
    # Get the video
    cap = cv2.VideoCapture(video)

    number_of_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Get the frames
    frames = []
    for i in range(number_of_frames):
        ret, frame = cap.read()
        if ret and i % frame_interval == 0:
            frames.append(frame)
    cap.release()
    return frames

def save_frames(frames, video_name):
    for i, frame in enumerate(frames):
        cv2.imwrite(f'{image_path}/{video_name}/frame_{FRAMES_PER_IMAGE*i+1}.jpg', frame)

def main():
    videos = os.listdir(video_path)
    videos.remove('.gitkeep')

    for video in videos:
        try:
            os.mkdir(f'{image_path}/{video}')
        except FileExistsError:
            pass
        frames = get_frames(f'{video_path}/{video}', FRAMES_PER_IMAGE)
        save_frames(frames, video)

if __name__ == '__main__':
    main()