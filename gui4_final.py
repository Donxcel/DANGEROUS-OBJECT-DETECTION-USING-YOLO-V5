import cv2
import threading
import tempfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from inference_sdk import InferenceHTTPClient
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from playsound import playsound
import time

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="ENTER_YOUR_API_KEY"
)

# Function to send image to Roboflow API and get inference results
def infer_image(image_path, model_id):
    result = CLIENT.infer(image_path, model_id=model_id)
    return result

# Function to send an email
last_email_time = 0
EMAIL_COOLDOWN = 60
def send_email_alarm(subject, body):
    global last_email_time
    playsound('alarm.wav')
    current_time = time.time()
    
    # Check if we can send an email for this object type
    if current_time - last_email_time > EMAIL_COOLDOWN:
        last_email_time = current_time
    sender_email = "legimadonxcel123@gmail.com"
    receiver_email = "legimadonal@gmail.com"
    password = "kvqgbgbiouxddndg"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

# Thread function to process inference
def process_frame(frame, model_id):
    global inference_result, processing_frame
    # Save frame to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        temp_filename = temp_file.name
        cv2.imwrite(temp_filename, frame)
    inference_result = infer_image(temp_filename, model_id)
    processing_frame = False

# Function to play alarm sound
def trigger_alarm():
    playsound('alarm.wav')  # Path to your alarm sound file

# Initialize the camera
cap = None

model_id = "multi-class-weapon-detection-system-github-zcv24/3"

inference_result = None
processing_frame = False
results_lock = threading.Lock()
grayscale = False

# Tkinter setup
root = tk.Tk()
root.title("Dangerous Object Detection")
root.geometry("1200x700")
root.configure(bg='#2c3e50')  # Modern dark background color

# Create a frame for buttons and log
control_frame = ttk.Frame(root, padding="10 10 10 10")
control_frame.pack(side=tk.TOP, fill=tk.X)

# Create a frame for the camera feed
camera_frame = ttk.Frame(root, padding="10 10 10 10")
camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a label to display the camera feed
label = ttk.Label(camera_frame)
label.pack()

# Create a frame for the side panel with a fixed width
side_panel_frame = ttk.Frame(root, padding="10 10 10 10", width=300)
side_panel_frame.pack_propagate(False)
side_panel_frame.pack(side=tk.RIGHT, fill=tk.Y)

# Create a text box for logging detected objects
log_text = tk.Text(root, height=10, state='disabled', bg='#ecf0f1', fg='black')  # Light background for text box
log_text.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

# Create a label to display the detected object description
description_label = tk.Label(side_panel_frame, text="Object Description", bg='#ecf0f1', fg='black', anchor='nw', justify='left', wraplength=280, font=('Arial', 14, 'bold'))
description_label.pack(fill=tk.BOTH, expand=True)

# Create a label for danger sign
danger_label = tk.Label(root, text="DANGER!", bg='red', fg='white', font=('Arial', 24, 'bold'))
danger_label.pack_forget()  # Initially hidden

# Function to show the danger sign for 5 seconds
def show_danger_sign():
    danger_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
    root.after(5000, danger_label.pack_forget)

# Function to start the camera feed
def start_camera():
    global cap
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # Set width
    cap.set(4, 480)  # Set height
    start_button.pack_forget()
    status_label.config(text="Camera On")
    update_frame()

# Function to stop the camera feed
def stop_camera():
    global cap
    if cap:
        cap.release()
    cap = None
    status_label.config(text="Camera Off")
    root.quit()

# Function to reset the log
def reset_log():
    log_text.config(state='normal')
    log_text.delete('1.0', tk.END)
    log_text.config(state='disabled')

# Function to toggle grayscale mode
def toggle_grayscale():
    global grayscale
    grayscale = not grayscale
    grayscale_button.config(text="Grayscale: On" if grayscale else "Grayscale: Off")

# Create start and stop buttons with colors
start_button = tk.Button(control_frame, text="Start", command=start_camera, bg='#27ae60', fg='white', font=('Arial', 12, 'bold'))
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(control_frame, text="Stop", command=stop_camera, bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'))
stop_button.pack(side=tk.LEFT, padx=10)

reset_button = tk.Button(control_frame, text="Reset Log", command=reset_log, bg='#2980b9', fg='white', font=('Arial', 12, 'bold'))
reset_button.pack(side=tk.LEFT, padx=10)

grayscale_button = tk.Button(control_frame, text="Grayscale: Off", command=toggle_grayscale, bg='#7f8c8d', fg='white', font=('Arial', 12, 'bold'))
grayscale_button.pack(side=tk.LEFT, padx=10)

# Create a label to show the camera status
status_label = ttk.Label(control_frame, text="Camera Off")
status_label.pack(side=tk.LEFT, padx=10)

# Object descriptions and danger levels
object_descriptions = {
    'Knife': "Knife: A knife is a sharp tool used for cutting. It can be dangerous if used as a weapon.",
    'Long-guns': "Long-gun: A Long-gun is a firearm designed to be fired from the shoulder. It is capable of inflicting serious injury.",
    'Handgun': "Handgun: A Handgun is a small firearm designed for one-handed use. It is highly dangerous and can cause fatal injuries.",
    'Sword': "Sword: This weapon as the symbol of military power, punitive justice, authority"
}

object_danger_levels = {
    'Knife': "Level of Danger: High",
    'Long-guns': "Level of Danger: Very High",
    'Handgun': "Level of Danger: Very High",
    'Sword': "Level of Danger: Very High"
}

def update_description(class_name):
    description = object_descriptions.get(class_name, "No description available.")
    danger_level = object_danger_levels.get(class_name, "Danger level unknown.")
    description_label.config(text=f"{description}\n\n{danger_level}")

def update_frame():
    global processing_frame

    if cap:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            return

        # Convert frame to grayscale if the option is selected
        if grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # Convert back to BGR for consistency

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (320, 240))

        # Start a new thread to process inference if not already processing
        if not processing_frame:
            processing_frame = True
            threading.Thread(target=process_frame, args=(small_frame, model_id)).start()

        # Process the results (you can customize this part based on the API response structure)
        with results_lock:
            if inference_result:
                for prediction in inference_result.get('predictions', []):
                    x, y, width, height = prediction['x'], prediction['y'], prediction['width'], prediction['height']
                    confidence = prediction['confidence']
                    class_name = prediction['class']
                    
                    # Check if the object is a knife, shotgun, or hand pistol with confidence > 0.6
                    if class_name in ['Knife', 'Long-guns', 'Handgun', 'Sword'] and confidence > 0.6:
                        email_subject = "Dangerous Object Detected"
                        email_body = f"A {class_name} has been detected with a confidence of {confidence:.2f}.\nDescription: {object_descriptions[class_name]}"   
                      
                        threading.Thread(target=send_email_alarm,args=(email_subject,email_body)).start()
                        show_danger_sign()
                        # Log detected object
                        log_text.config(state='normal')
                        log_text.insert(tk.END, f"Detected: {class_name} ({confidence:.2f})\n")
                        log_text.config(state='disabled')
                        update_description(class_name)

                    # Scale bounding box coordinates back to the original frame size
                    x = int(x * (640 / 320))
                    y = int(y * (480 / 240))
                    width = int(width * (640 / 320))
                    height = int(height * (480 / 240))
                    
                    # Draw bounding box and label on the frame
                    start_point = (int(x - width / 2), (int(y - height / 2)))
                    end_point = (int(x + width / 2), (int(y + height / 2)))
                    cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)
                    label_text = f"{class_name} ({confidence:.2f})"
                    cv2.putText(frame, label_text, (start_point[0], start_point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert frame to ImageTk format
        cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2_image)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update label with the new frame
        label.imgtk = imgtk
        label.configure(image=imgtk)

    # Schedule the next frame update
    root.after(10, update_frame)

# Run the Tkinter main loop
root.mainloop()

# Release the camera
if cap:
    cap.release()
cv2.destroyAllWindows()
