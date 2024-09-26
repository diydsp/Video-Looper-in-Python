import cv2
import numpy as np
import threading

class VideoStreamHandler:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        self.frame = None
        self.running = True

    def start_stream(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame from the camera.")
                break
            self.frame = frame

            # Display live video feed
            cv2.imshow('Live Camera Feed', self.frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_stream()
                break

    def get_current_frame(self):
        return self.frame

    def stop_stream(self):
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()


class FrameManager:
    def __init__(self):
        self.frames = [[], [], [], []]  # Four lists of frames for recording streams 1-4
        self.is_recording = False
        self.selected_stream = None  # Track which stream is being recorded
        self.indices = [0, 0, 0, 0]  # Indices for playback for each stream

    def start_recording(self, stream_number):
        self.is_recording = True
        self.selected_stream = stream_number - 1  # Map keys 1-4 to stream indices 0-3
        print(f"Recording started on stream {stream_number}...")

    def stop_recording(self):
        self.is_recording = False
        self.selected_stream = None
        print("Recording stopped.")

    def record_frame(self, frame):
        if self.is_recording and self.selected_stream is not None:
            # Record the current frame to the selected stream
            self.frames[self.selected_stream].append(frame)

    def playback_frame(self, stream_index):
        # Loop through the frames in the specified stream based on the index
        if len(self.frames[stream_index]) > 0:
            frame = self.frames[stream_index][self.indices[stream_index]]
            self.indices[stream_index] = (self.indices[stream_index] + 1) % len(self.frames[stream_index])
            return frame
        return np.zeros((240, 320, 3), dtype=np.uint8)  # Return a blank frame if no recorded frames

    def display_combined_frame(self):
        # Show the last recorded frames in a 2x2 grid
        playback_frames = [self.playback_frame(i) for i in range(4)]
        combined_frame = self.combine_frames(playback_frames)
        cv2.imshow('2x2 Video Grid', combined_frame)

    def combine_frames(self, frames):
        # Resize frames to fit in a 2x2 grid (320x240 as an example)
        resized_frames = [cv2.resize(frame, (320, 240)) for frame in frames]
        top_row = np.hstack((resized_frames[0], resized_frames[1]))  # Stack top row
        bottom_row = np.hstack((resized_frames[2], resized_frames[3]))  # Stack bottom row
        combined_frame = np.vstack((top_row, bottom_row))  # Combine into 2x2 grid
        return combined_frame


def main():
    # Initialize both the camera stream handler and the frame manager
    stream_handler = VideoStreamHandler(source=0)
    frame_manager = FrameManager()

    # Start the camera stream in a separate thread
    threading.Thread(target=stream_handler.start_stream).start()

    while True:
        key = cv2.waitKey(1) & 0xFF

        if key == ord('1'):
            frame_manager.start_recording(1)  # Start recording on stream 1
        elif key == ord('2'):
            frame_manager.start_recording(2)  # Start recording on stream 2
        elif key == ord('3'):
            frame_manager.start_recording(3)  # Start recording on stream 3
        elif key == ord('4'):
            frame_manager.start_recording(4)  # Start recording on stream 4
        elif key == ord('s'):
            frame_manager.stop_recording()  # Stop recording
        elif key == ord('q'):
            stream_handler.stop_stream()  # Quit the program
            break

        # Get the current frame from the camera and record it if needed
        current_frame = stream_handler.get_current_frame()
        if current_frame is not None:
            frame_manager.record_frame(current_frame)

        # If not recording, show the playback of recorded streams
        if not frame_manager.is_recording:
            frame_manager.display_combined_frame()


if __name__ == "__main__":
    main()
