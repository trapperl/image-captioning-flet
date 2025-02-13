# Image Captioning Tool

## Overview
The **Image Captioning Tool** is a desktop application built with [Flet](https://flet.dev/) that allows users to:

- Load images from a selected folder
- Generate AI-based captions using OpenAI's GPT-4o
- Manually edit and save captions
- Manage and apply tags to images

This tool is useful for creating descriptive captions for images, which can be used for AI training datasets, content generation, or organizing large image collections.

## Features
- **Folder Selection:** Load a directory of images.
- **Thumbnail Navigation:** Browse images via a sidebar of thumbnails.
- **AI-Powered Captioning:** Generate captions using OpenAI's GPT-4o.
- **Manual Captioning:** Edit and save captions.
- **Tag Management:** Add, edit, and delete tags.
- **Settings Panel:** Configure OpenAI API key and caption prompt.
- **Dark Mode UI:** Optimized for visual comfort.

## Installation
### Prerequisites
Ensure you have Python installed (>=3.8) and install dependencies:

```sh
pip install flet openai python-dotenv
```

### Environment Variables
Create a `.env` file in the root directory and add your OpenAI API key:

```ini
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage
Run the application with:

```sh
python src/main.py
```

### Steps
1. Click **Select Folder** to load images.
2. Click on an image thumbnail to view it.
3. Enter a caption manually or click **Generate Caption**.
4. Save captions with the **Save Caption** button.
5. Manage tags to organize images.

## Configuration
- **API Key:** Enter your OpenAI API key in the settings panel.
- **Prompt Customization:** Modify the captioning prompt in the settings panel.
- **Tagging System:** Edit and apply tags for image classification.

## Troubleshooting
- **No captions generated?** Ensure your OpenAI API key is valid and has sufficient credits.
- **Images not loading?** Verify the folder contains image files (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`).
- **Missing `.env` file?** Create one and add your API key.

## License
This project is licensed under the MIT License.

## Author
Developed by Trapper Leabo.

