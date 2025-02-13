# README.md

# Image Captioning Flet

## Overview
Image Captioning Flet is a Python application designed to provide an interactive interface for displaying images and generating captions. The application utilizes various components to manage image viewing and user input for captions.

## Project Structure
```
image-captioning-flet
├── src
│   ├── main.py               # Main application logic
│   └── components            # Reusable UI components
│       ├── __init__.py       # Package initialization
│       ├── image_viewer.py   # Component for displaying images
│       └── caption_input.py   # Component for handling caption input
├── assets                     # Directory for assets
│   └── .gitkeep               # Keeps the assets directory in version control
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
└── .gitignore                 # Files to ignore in version control
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd image-captioning-flet
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source .venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python src/main.py
```

Follow the on-screen instructions to display images and input captions.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.