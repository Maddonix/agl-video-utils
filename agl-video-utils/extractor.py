import cv2
import os
from pathlib import Path
from tqdm import tqdm

class FrameExtractor:
    def __init__(self, video_path: Path):
        assert video_path.suffix == '.mp4', "Video file must be a .mp4 file"
        self.video_path = video_path

    def extract_frames(self, frame_interval: int = 1):
        # Open the video file
        video = cv2.VideoCapture(str(self.video_path))
        
        # Get the frames per second
        fps = video.get(cv2.CAP_PROP_FPS)

        # Get the total number of frames
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        # Calculate number of frames to extract
        num_frames_to_extract = total_frames // frame_interval

        # Get the video filename without the extension
        filename = self.video_path.stem

        # Create a new directory to save the frames
        frame_dir = Path(f"frames_{filename}_{fps}")
        frame_dir.mkdir(parents=True, exist_ok=True)

        # Initialize progress bar
        pbar = tqdm(total=num_frames_to_extract)

        frame_count = 0
        extracted_count = 0
        while video.isOpened():
            success, frame = video.read()
            # If the frame was successfully read
            if success:
                if frame_count % frame_interval == 0:
                    # Save the frame to a jpeg file
                    frame_file = frame_dir / f"{frame_count}.jpeg"
                    cv2.imwrite(str(frame_file), frame)
                    extracted_count += 1
                    pbar.update(1)
                frame_count += 1
            else:
                break
        video.release()
        pbar.close()
