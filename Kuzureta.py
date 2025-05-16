import cv2
import os
import sys
import threading
from queue import Queue

# ASCII characters used to represent pixel intensity
ASCII_CHARS = "@%#*+=-:. "

def grayify(image):
    """Convert image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def pixels_to_ascii(image):
    """Map pixel values to ASCII characters."""
    ascii_image = []
    for row in image:
        ascii_row = [ASCII_CHARS[pixel // 25] for pixel in row]
        ascii_image.append("".join(ascii_row))
    return "\n".join(ascii_image)

def resize_image(image, width=100):
    """Resize image to fit within the terminal width."""
    height, width_orig = image.shape[:2]
    aspect_ratio = height / width_orig
    new_height = int(width * aspect_ratio * 0.55)
    resized_image = cv2.resize(image, (width, new_height), interpolation=cv2.INTER_AREA)
    return resized_image

def convert_frame_to_ascii(frame, width=100):
    """Convert a single video frame to ASCII."""
    gray_frame = grayify(frame)
    resized_frame = resize_image(gray_frame, width)
    ascii_frame = pixels_to_ascii(resized_frame)
    return ascii_frame

def process_frames(video_path, frame_queue, width=100):
    """Read and process video frames."""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Cannot open video.")
        sys.exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            ascii_frame = convert_frame_to_ascii(frame, width)
            frame_queue.put(ascii_frame)
        except Exception as e:
            print(f"Error processing frame: {e}")
            break

    cap.release()
    frame_queue.put(None)  # Signal the end of frames

def play_ascii_frames(frame_queue, fps):
    """Play ASCII frames from the queue."""
    while True:
        ascii_frame = frame_queue.get()
        if ascii_frame is None:
            break
        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_frame)
        cv2.waitKey(max(1, int(1000 / fps)))

def main():
    try:
        video_path = input("Enter the path to the video file: ").strip()
        width = int(input("Enter the desired width of ASCII art (default 100): ") or 100)
        fps = int(input("Enter the desired playback FPS (default 30): ") or 30)

        if not os.path.exists(video_path):
            print(f"Error: File {video_path} does not exist.")
            return

        frame_queue = Queue(maxsize=10)

        # Start threads for processing and playing
        processing_thread = threading.Thread(target=process_frames, args=(video_path, frame_queue, width))
        playing_thread = threading.Thread(target=play_ascii_frames, args=(frame_queue, fps))

        processing_thread.start()
        playing_thread.start()

        processing_thread.join()
        playing_thread.join()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
