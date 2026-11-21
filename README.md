# OptoReader

A desktop app that reads text aloud for visually impaired users. Point a webcam at a printed page, or open a PDF, and OptoReader extracts the text and speaks it.

> Built as an internship project.


## Table of contents

- [Overview](#overview)
- [Features](#features)
- [How it works](#how-it-works)
- [Tech stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Keyboard shortcuts](#keyboard-shortcuts)
- [Project structure](#project-structure)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [Future improvements](#future-improvements)
- [License](#license)

## Overview

Reading printed material is difficult for people with low vision or blindness. OptoReader turns a normal laptop or PC into a simple reading aid. It has two modes:

1. **Scan Image to Read.** Shows a live camera feed. Hold a document in front of the camera, press a button or the Enter key, and the app reads the text aloud.
2. **Choose PDF to Read.** Pick a PDF from your computer. The app extracts its text, shows it on screen and reads it aloud on request.

All processing happens on your own machine. No internet connection or cloud service is needed.

## Features

**Scan Image to Read**
- Live webcam preview (640 x 480)
- One-click or Enter-key capture
- OCR on the captured frame using Tesseract
- Result shown on screen and spoken automatically
- Spoken error message if no text is found
- Clear button to stop speech and reset the result

**Choose PDF to Read**
- File picker to choose any PDF
- Text extracted from every page
- Scrollable view of the extracted text
- "Read Extraction" button to speak the text
- Clear button to stop speech and reset

**General**
- Offline text-to-speech with a slightly slower speaking rate for clarity
- Speech and OCR run in background threads so the window stays responsive
- Full-screen reading windows with keyboard shortcuts
- Simple home screen with two large buttons

## How it works

```
Camera mode
  Webcam frame --> saved as temp_image1.jpg --> Tesseract OCR --> text
                                                                   |
                                          shown on screen <--------+--------> spoken by pyttsx3

PDF mode
  PDF file --> PyMuPDF (page by page) --> text --> shown on screen --> spoken by pyttsx3 on request
```

## Tech stack

| Purpose | Library |
|---|---|
| GUI | CustomTkinter, Tkinter |
| Camera capture | OpenCV (`cv2`) |
| Image handling | Pillow |
| OCR | pytesseract (wrapper for the Tesseract OCR engine) |
| PDF text extraction | PyMuPDF (`fitz`) |
| Text to speech | pyttsx3 (offline) |
| Concurrency | `threading`, `queue` |

## Prerequisites

- Python 3.9 or newer
- A working webcam (for image mode)
- Speakers or headphones
- **Tesseract OCR engine** installed on your system. The `pytesseract` package is only a wrapper and does not include the engine.
  - **Windows:** download the installer from the [UB Mannheim Tesseract builds](https://github.com/UB-Mannheim/tesseract/wiki) and add the install folder to your `PATH`.
  - **macOS:** `brew install tesseract`
  - **Ubuntu/Debian:** `sudo apt install tesseract-ocr`

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/ravindra11-jpg/optoreader.git
cd optoreader

# 2. (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install the Python dependencies
pip install opencv-python pytesseract pyttsx3 pillow customtkinter pymupdf
```

Check that Tesseract is reachable:

```bash
tesseract --version
```

## Usage

```bash
python optoreader.py
```

The home window opens with two buttons.

### Read from the camera

1. Click **Scan Image to Read**.
2. Place the document in the centre of the camera view. Good light and a flat page give the best results.
3. Press **SCAN and READ** or the **Enter** key.
4. The extracted text appears on the right and is read aloud.
5. Click **clear** to stop speaking and reset, or **Exit Application** to return to the home screen.

### Read a PDF

1. Click **Choose PDF to Read**.
2. Click **Scan and Extract** and choose a PDF file.
3. Review the text on screen.
4. Click **Read Extraction** to hear it.
5. Click **clear** to reset, or **exit** to return home.

## Keyboard shortcuts

| Key | Where | Action |
|---|---|---|
| `Enter` | Camera window | Scan and read |
| `Esc` | Camera window | Return to home screen |
| `Esc` | PDF window | Return to home screen |
| `Esc` | Home screen | Quit the app |

## Project structure

```
optoreader/
├── optoreader.py    # the whole application: GUI, camera, OCR, PDF reading, speech
└── README.md
```

Temporary file: while scanning, each captured frame is saved as `temp_image1.jpg` in the folder you run the app from, and it is overwritten on every scan.

## Known limitations

- **Scanned PDFs are not supported yet.** PDF mode reads the PDF's text layer. A PDF that is only a picture of a page returns no text.
- **OCR quality depends on the image.** Blur, glare, shadows, a tilted page or handwriting reduce accuracy.
- **English by default.** Tesseract uses its English model unless more languages are installed and configured in the code.
- **Camera index 0 only.** The app opens the first camera on the system.
- **Voice and speed are fixed.** The first installed system voice is used at a reduced rate.
- **No pause or resume.** Speech can be stopped with **clear**, but not paused.
- **Windows PATH.** The code does not set the Tesseract path, so Tesseract must be on `PATH`.

## Troubleshooting

| Problem | Likely fix |
|---|---|
| `TesseractNotFoundError` | Install the Tesseract engine and add it to `PATH`, then restart the terminal. |
| Camera window is black or shows "No frame captured" | Close other apps using the camera, then check that the camera works elsewhere. |
| No sound | Check system volume and that a speech voice is installed (SAPI5 on Windows, NSSpeechSynthesizer on macOS, `espeak` on Linux). |
| `No text was recognized` | Improve lighting, hold the page flat and steady, move it closer to the camera. |
| Poor accuracy | Use a printed page with clear, dark text on a plain light background. |

## Future improvements

- OCR fallback for image-only PDFs
- Multi-language OCR and voice selection
- Adjustable speech speed, pause and resume
- Image pre-processing (grayscale, thresholding, deskew) for better accuracy
- Voice prompts so the full interface is usable without sight
- A `requirements.txt` and packaged executable

## License

Add a license of your choice (for example MIT) before sharing the project publicly.
