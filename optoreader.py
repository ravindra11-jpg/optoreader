import pytesseract
import cv2
import pyttsx3
import threading
import queue
from PIL import Image
import customtkinter as ctk
import fitz  # PyMuPDF
import tkinter
from tkinter import filedialog

# Environment Setup
result_queue = queue.Queue()
temp_image_path = "temp_image1.jpg"
exit_flag = False
video_label = None
frame = None  # Declare a global frame variable
thread_stop_event = threading.Event()
engine = None
ocr_thread = ""
text = ""
pdf_path = ""

# Camera Properties 
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)



'''FUNCTIONS FOR SCANNING FROM CAMERA SOURCE'''
# Extract text from the frame
def extract_text(temp_image_path, frame, result_queue):
    try:
        cv2.imwrite(temp_image_path, frame)
        text = pytesseract.image_to_string(temp_image_path)
        if text.strip() == "":
            result_queue.put({"error": "No text was recognized. Please try again."})
        else:
            result_queue.put({"text": text})
    except Exception as e:
        result_queue.put({"error": str(e)})

#helper function for saying out result queue
def speak_text(text):
    global engine, thread_stop_event
    try:
        if engine is None:
            engine = pyttsx3.init()
            engine.setProperty('rate', engine.getProperty('rate') - 30)  # Adjust speech rate if needed
            engine.setProperty('voice', engine.getProperty('voices')[0].id)  # Set voice to default
        engine.say(text)  # Add each word to the speech queue
        engine.runAndWait()  # Process the queue after each chunk
        engine.stop()
    except Exception as e:
        print(f"Error during speech synthesis: {e}")

# Process the image and update the result label
def process_image(temp_image_path, result_queue, result_label):
    global frame, thread_stop_event
    if frame is None:
        result_label.configure(text="No frame captured. Please try again.") 
        return
    result_label.configure(text="Processing...")
    #funciton runs 'extract_text' function and gets result from it to update to result label and speak_text function
    def run_ocr():
        while not thread_stop_event.is_set(): #if flag is not true
            extract_text(temp_image_path, frame, result_queue) #running extract text function
            
            if not result_queue.empty(): # Check the result queue and update the result label
                result = result_queue.get()
                if "error" in result:
                    result_label.configure(text=result["error"])
                    error = result["error"]
                    threading.Thread(target=speak_text, args=(error,), daemon=True).start()
                elif "text" in result:
                    result_label.configure(text=f"Extracted Text: {result['text']}")
                    text = result["text"]
                    threading.Thread(target=speak_text, args=(text,), daemon=True).start()
                break
            if thread_stop_event.is_set():  # Exit if stop event is set (in exit application button)
                break

    thread_stop_event.clear()  # Reset the stop signal before starting the thread
    ocr_thread = threading.Thread(target=run_ocr, daemon=True)
    ocr_thread.start() #running run_ocr in thread to avoid GIL with GUI

# Exit the scan window and return to root
def exit_application(scanimage_window):
    global exit_flag, thread_stop_event
    thread_stop_event.set()
    exit_flag = True
    if cam.isOpened():
        cam.release() 
    if engine:
        engine.stop()
    scanimage_window.destroy()
    root.deiconify()

# Ensure thread_stop_event is set when the window is closed unexpectedly
def clear_ocrdata(result_label):
    global engine
    if engine:
        engine.stop()
    result_queue.queue.clear()
    result_label.configure(text = "Scan frame to read")


# Start updating the video feed using after()
def update_video(scanimage_window):
    global frame, video_label
    if exit_flag:
        return
    ret, frame = cam.read()
    if ret:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        ctk_image = ctk.CTkImage(img, size=(640, 480))
        video_label.imgtk = ctk_image
        video_label.configure(image=ctk_image)
    if not exit_flag:
        scanimage_window.after(10, lambda: update_video(scanimage_window))



'''MAIN SCAN IMAGE GUI FUNCTION - mapped to 'scan image' at homescreen'''
def scanimageoption():
    global video_label,exit_flag, cam
    exit_flag = False
    root.withdraw()
    if not cam.isOpened():
        cam = cv2.VideoCapture(0)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    scanimage_window = ctk.CTkToplevel(root)
    scanimage_window.title("OptoReader - Scan Image")
    scanimage_window.attributes('-fullscreen',True)
    scanimage_window.protocol("WM_DELETE_WINDOW", lambda: exit_application(scanimage_window))
    
    # Configure rows and columns to make the layout responsive
    for i in range(20):  
        scanimage_window.grid_rowconfigure(i, weight=1)  
        scanimage_window.grid_columnconfigure(i, weight=1)  

    # Video Label 
    video_frame = ctk.CTkFrame(scanimage_window, border_width=2, border_color="darkgray")
    video_frame.grid(row=1, column=1, rowspan = 12 , columnspan=7, sticky="nsew", padx=1, pady=5)
    video_label = ctk.CTkLabel(video_frame, text="Place document at the center")
    video_label.pack(fill="both", expand=True, padx=1, pady=1)

    # Result Label 
    result_frame = ctk.CTkFrame(scanimage_window, border_width=2, border_color="darkgray")
    result_frame.grid(row=0, column=11, rowspan=20, columnspan=6, sticky="nsew", padx=10, pady=10)

    result_label = ctk.CTkLabel(result_frame, text="Results will appear here", wraplength=600)
    result_label.pack(fill="both", expand=False, padx=5, pady=5)

    clear_button = ctk.CTkButton(result_frame, text = "clear", command = lambda: clear_ocrdata(result_label))
    clear_button.pack(fill = "none", side = "bottom", padx = 5, pady=5)

    #button frame
    button_frame = ctk.CTkFrame(scanimage_window)
    button_frame.grid(row=16, column= 4, sticky="nsew", padx=5, pady=5)

    button_frame.grid_rowconfigure(0, weight=1)  # Row for first button
    button_frame.grid_rowconfigure(1, weight=1)  # Row for second button
    button_frame.grid_columnconfigure(0, weight=3)  # First column in button frame
    button_frame.grid_columnconfigure(1, weight=3)  # Second column in button frame
    
    scanimage_window.bind('<Return>', lambda event: process_image(temp_image_path, result_queue, result_label)) #key bind - enter for image processing
    capture_button = ctk.CTkButton(
        button_frame,
        text="SCAN and READ",
        command=lambda: process_image(temp_image_path, result_queue, result_label),
        border_color="darkgray"
    )
    capture_button.grid(row = 0, column = 0, rowspan = 2 ,sticky = "nsew", ipadx = 15, padx=1, pady=5)

    # Exit Button
    scanimage_window.bind('<Escape>', lambda event: exit_application(scanimage_window)) #keybind esc for exiting
    exit_button = ctk.CTkButton(
        button_frame,
        text="Exit Application",
        command=lambda: exit_application(scanimage_window),
        border_color="darkgray"
    )
    exit_button.grid(row = 0, column = 2, sticky = "nsew",rowspan = 2 , ipadx = 15,  padx=1, pady=5)
    #running update window 
    update_video(scanimage_window)



'''FUNCTIONS FOR PDF SCANNING'''
#text extraction - called insde process_pdf()
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)  # Open the PDF
    text = ""
    # Iterate through each page and extract text
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()  # Extract text from the page
    return text

#function for voice engine - mapped to read_button
def read_text_aloud(text):
    global  engine
    if engine is None:
        engine = pyttsx3.init()
        engine.setProperty('rate', engine.getProperty('rate') - 30)  # Adjust speech rate if needed
        engine.setProperty('voice', engine.getProperty('voices')[0].id)  # Set voice to default
    engine.say(text)  # Speak the text
    engine.runAndWait()  # Wait for the speech to finish
    engine.stop()  # Stop the speech engine

#main processing function - mapped to scan_button
def process_pdf(result_label):
    global text
    tkinter.Tk().withdraw()
    pdf_path = filedialog.askopenfilename() #choosing filepath
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)
    # Printing in the display label
    result_label.configure(text = text)

#overall exit function(exits to homescreen) - mapped to Exit_button
def exit_readpdf(readpdf_window):
    global engine
    if engine:
        engine.stop()
    readpdf_window.destroy()
    root.deiconify()

#immediate reset function - mapped to reset_button
def reset_function(result_label):
    global engine
    if engine:
        engine.stop()
    text = ""
    pdf_path = ""
    result_label.configure(text = "choose pdf to read")
    return text, pdf_path
    
    

'''GUI FOR PDF SCAN WINDOW'''
def scanPDFoption():
    root.withdraw()
    readpdf_window = ctk.CTkToplevel(root)
    readpdf_window.title("OptoReader - Scan PDF")
    readpdf_window.attributes('-fullscreen',True)
    readpdf_window.protocol("WM_DELETE_WINDOW", lambda: exit_readpdf(readpdf_window))

    for i in range(20):  # Adjust the range based on your layout needs
        readpdf_window.grid_rowconfigure(i, weight=1)  # Make all rows responsive
        readpdf_window.grid_columnconfigure(i, weight=1)  # Make all columns responsive

    # Result Label with border simulated using CTkFrame
    result_frame = ctk.CTkScrollableFrame(readpdf_window, border_width=2, border_color="darkgray")
    result_frame.grid(row=1, column=3, rowspan=10, columnspan=14, sticky="nsew", padx=10, pady=10)
    readpdf_window.bind('<Escape>', lambda event: exit_readpdf(readpdf_window))

    result_label = ctk.CTkLabel(result_frame, text="Results will appear here", wraplength=600)
    result_label.pack(fill="both", expand=True, padx=5, pady=10)

    button_frame = ctk.CTkFrame(readpdf_window)
    button_frame.grid(row=15, column= 10, sticky="nsew", padx=5, pady=5)

    # Configure grid layout for button_frame to center buttons
    button_frame.grid_rowconfigure(0, weight=1, uniform="equal")  # Single row with equal weight
    button_frame.grid_columnconfigure(0, weight=1, uniform="equal")  # Set equal space for all columns
    button_frame.grid_columnconfigure(1, weight=1, uniform="equal")
    button_frame.grid_columnconfigure(2, weight=1, uniform="equal")
    button_frame.grid_columnconfigure(3, weight=1, uniform="equal")

    Scan_button = ctk.CTkButton(
        button_frame,
        text="Scan and Extract",
        command=lambda: process_pdf(result_label),
        border_color="darkgray"
    )
    Scan_button.grid(row = 0, column = 0,sticky = "nsew", padx=10, pady=5)

    read_button = ctk.CTkButton(
        button_frame,
        text="Read Extraction",
        command=lambda: threading.Thread(target= read_text_aloud, args=(text,)).start(),
        border_color="darkgray"
    )
    read_button.grid(row = 0, column = 1,sticky = "nsew", padx=10, pady=5)

    reset_button= ctk.CTkButton(
        button_frame,
        text="clear",
        command=lambda: reset_function(result_label),
        border_color="darkgray"
    )
    reset_button.grid(row = 0, column = 2,sticky = "nsew", padx=10, pady=5)

    exit_button= ctk.CTkButton(
        button_frame,
        text="exit",
        command=lambda: exit_readpdf(readpdf_window),
        border_color="darkgray"
    )
    exit_button.grid(row = 0, column = 3,sticky = "nsew", padx=10, pady=5)

    

'''HOME SCREEN GUI'''
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("OptoReader - HOME")


def center_window(window, width, height):
    # Get the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the position to center the window
    position_top = int(screen_height / 2 - height / 2)
    position_right = int(screen_width / 2 - width / 2)

    # Set the window size and position
    window.geometry(f'{width}x{height}+{position_right}+{position_top}')


# Set the window size
window_width = 600
window_height = 450

# Center the window
center_window(root, window_width, window_height)

# Configure rows and columns for responsiveness
root.rowconfigure(0, weight=3)  # Title occupies more vertical space
root.rowconfigure(1, weight=1)  # Space between title and buttons
root.rowconfigure(2, weight=1)  # First button
root.rowconfigure(3, weight=1)  # Second button
root.columnconfigure(0, weight=1)  # Single column layout

# Title Label
title_label = ctk.CTkLabel(
    root,
    text="OptoReader",
    font=("Eras Bold ITC", 46),
    anchor="center",
)
title_label.grid(row=0, column=0, sticky="nsew", pady=(50, 10))  # Centered with padding

# Buttons
scan_button = ctk.CTkButton(
    root,
    text="Scan Image to Read",
    command=scanimageoption,
)
scan_button.grid(row=1, column=0, sticky="nsew", padx=50, pady=10)

pdf_button = ctk.CTkButton(
    root,
    text="Choose PDF to Read",
    command=scanPDFoption,
)
pdf_button.grid(row=2, column=0, sticky="nsew", padx=50, pady=10)
# Run the application
root.bind('<Escape>', lambda event: root.destroy())  

root.mainloop()