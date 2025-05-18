import cv2
import os
import sys
import threading
from queue import Queue
import time

# ASCII characters used to represent pixel intensity
ASCII_CHARS = "@%#*+=-:. "

def grayify(image):
    """Convert image to grayscale."""
    if image is None or image.size == 0:
        raise ValueError("Invalid image data for grayscale conversion.")
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def pixels_to_ascii(image):
    """Map pixel values to ASCII characters."""
    if image is None or len(image) == 0:
        raise ValueError("Invalid image data for ASCII conversion.")
    ascii_image = []
    for row in image:
        ascii_row = []
        for pixel in row:
            try:
                ascii_row.append(ASCII_CHARS[pixel // 25])
            except IndexError:
                ascii_row.append(" ")  # Default to space for unexpected values
        ascii_image.append("".join(ascii_row))
    return "\n".join(ascii_image)

def resize_image(image, width, height):
    """Resize image to fit the specified width and height."""
    if image is None or image.size == 0:
        raise ValueError("Invalid image data for resizing.")
    resized_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return resized_image

def convert_frame_to_ascii(frame, width, height):
    """Convert a single video frame to ASCII."""
    try:
        gray_frame = grayify(frame)
        resized_frame = resize_image(gray_frame, width, height)
        ascii_frame = pixels_to_ascii(resized_frame)
        return ascii_frame
    except Exception as e:
        raise RuntimeError(f"Error in frame conversion: {e}")

def process_frames(video_path, frame_queue, width, height):
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
            ascii_frame = convert_frame_to_ascii(frame, width, height)
            frame_queue.put(ascii_frame)
        except Exception as e:
            print(f"Warning: Frame processing failed. {e}")
            # Push a blank frame to avoid interruption
            blank_frame = "\n".join([" " * width for _ in range(height)])
            frame_queue.put(blank_frame)

    cap.release()
    frame_queue.put(None)  # Signal the end of frames

def play_ascii_frames(frame_queue, fps):
    """Play ASCII frames from the queue."""
    frame_delay = 1 / fps
    while True:
        start_time = time.time()
        ascii_frame = frame_queue.get()
        if ascii_frame is None:
            break

        # Clear the console screen
        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_frame)

        # Calculate elapsed time and wait for remaining frame time
        elapsed_time = time.time() - start_time
        remaining_time = max(0, frame_delay - elapsed_time)
        time.sleep(remaining_time)

def main():
    try:
        video_path = input("Enter the path to the video file: ").strip()

        if not os.path.exists(video_path):
            print(f"Error: File {video_path} does not exist.")
            return

        width = int(input("Enter the desired frame width (e.g., 100): ").strip())
        height = int(input("Enter the desired frame height (e.g., 40): ").strip())
        fps = int(input("Enter the desired playback FPS (default 30): ").strip() or 30)

        frame_queue = Queue(maxsize=100)  # Increased buffer size to prevent bottlenecks

        # Start threads for processing and playing
        processing_thread = threading.Thread(target=process_frames, args=(video_path, frame_queue, width, height))
        playing_thread = threading.Thread(target=play_ascii_frames, args=(frame_queue, fps))

        processing_thread.start()
        playing_thread.start()

        # Ensure both threads complete before program exits
        processing_thread.join()
        playing_thread.join()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
