import ttkbootstrap as tb
from ttkbootstrap.constants import *

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import cv2
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode

import queue
import time
import platform
import winsound
import threading
import qrcode
set_theme = "pulse"
_bg ='plum1'
_bg2 = " "
_fg = "bisque"
b_style ='light'
window_width = 700
window_height = 530

class WebcamScanner:
    def __init__(self, video_label, sound_path="beep.mp3", width=640, height=480, camera_index=0):
        """
        Initializes the webcam scanner with customizable options.
        
        Parameters:
            video_label (tk.Label): The label to display the webcam feed.
            sound_path (str): Path to the sound file to play on QR code detection.
            width (int): Width of the webcam feed.
            height (int): Height of the webcam feed.
            camera_index (int): Index of the webcam to use (default is 0).
        """
        self.video_label = video_label
        self.width = width
        self.height = height
        self.sound_path = sound_path
        self.camera_index = camera_index
        self.scanning = False
        self.running = True
        self.scanned_code = None
        self.lock = threading.Lock()  # Lock for thread-safe access to scanned_code

        # Queue for thread-safe frame passing
        self.frame_queue = queue.Queue(maxsize=1)

        # Open the specified webcam
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open webcam with index {self.camera_index}")
            return
        
        # Start video capture in a separate thread
        self.capture_thread = threading.Thread(target=self.capture_frames, daemon=True)
        self.capture_thread.start()

        # Start updating the GUI frame
        self.update_frame()

    def play_sound(self):
        """Plays a sound when a QR code is detected."""
        try:
            if platform.system() == "Windows":
                winsound.Beep(1000, 300)  # Frequency 1000 Hz, Duration 200 ms
            else:
                print("\a")  # Fallback beep for non-Windows systems
        except Exception as e:
            print(f"Error playing sound: {e}")

    def scan_qr(self):
        """Triggers QR code scanning on button press."""
        self.scanning = True

    def capture_frames(self):
        """Captures frames continuously in a separate thread."""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Resize the frame for consistency
                frame = cv2.resize(frame, (self.width, self.height))

                # Check for QR code when scanning is triggered
                if self.scanning:
                    decoded_objects = decode(frame)
                    for obj in decoded_objects:
                        data = obj.data.decode("utf-8")
                        if data.isdigit():
                            number = int(data)
                            print(f"Scanned Number: {number}")
                            self.play_sound()
                            with self.lock:
                                self.scanned_code = number  # Store scanned code
                            self.scanning = False  # Stop scanning after detecting
                            break

                # Put the frame into the queue if space is available
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)

            # Delay to reduce CPU usage
            time.sleep(0.01)

    def get_scanned_code(self):
        """Returns the last scanned QR code and resets it to None."""
        with self.lock:
            code = self.scanned_code
            self.scanned_code = None  # Reset after returning
            return code

    def update_frame(self):
        """Updates the tkinter label with the latest frame from the queue."""
        if not self.frame_queue.empty():
            frame = self.frame_queue.get()

            # Convert the frame to RGB and display it
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the tkinter label
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Schedule the next frame update
        self.video_label.after(10, self.update_frame)

    def stop(self):
        """Releases the webcam and stops the feed."""
        self.running = False
        self.capture_thread.join()
        self.cap.release()
        cv2.destroyAllWindows()


root = tb.Window(themename=set_theme)
style=ttk.Style()
root.title("QR-test")
lent = int((root.winfo_screenheight()/2)-window_height/2)
widt = int((root.winfo_screenwidth()/2)-window_width/2)
root.geometry("{}x{}+{}+{}".format(window_width,window_height,widt,lent))
root.minsize(window_width,window_height)
root.maxsize(window_width,window_height)

lab1 = ttk.Label(root)
scanner = WebcamScanner(lab1, width=350, height=400, camera_index=0)
lab1.pack()

root.mainloop()
