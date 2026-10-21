# Azure AI Vision — Cloud-Based Image Analysis

<p align="center">
  <strong>Upload an image. Analyze it in the cloud. Understand what it contains.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Web%20App-lightgrey?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/AI-Microsoft%20Azure%20AI%20Vision-0078D4?logo=microsoftazure" alt="Azure AI Vision">
  <img src="https://img.shields.io/badge/Interface-HTML%20%2B%20CSS-orange" alt="HTML and CSS">
</p>

A Python Flask web application that accepts an image uploaded by a user, sends it to **Microsoft Azure AI Vision**, and presents the returned image-analysis results in a simple web interface.

> **Interactive project page:** After enabling GitHub Pages, add your published site URL here. It will usually look like `https://YOUR-USERNAME.github.io/AzureImageAnalysis/`.

## Contents

- [Overview](#overview)
- [Interface preview](#interface-preview)
- [Features](#features)
- [How it works](#how-it-works)
- [Technology stack](#technology-stack)
- [Run locally](#run-locally)
- [Configuration and security](#configuration-and-security)
- [Project structure](#project-structure)
- [Limitations](#limitations)
- [Learning outcomes](#learning-outcomes)

## Overview

This project demonstrates a complete cloud computer-vision workflow:

1. A user selects an image in the browser.
2. Flask validates the upload and sends the image bytes to the Azure AI Vision REST API.
3. Azure analyzes the image and returns structured JSON.
4. The application extracts supported results and displays them in the browser.

The current interface was tested with a monochrome photograph of trees in fog. Azure returned the caption **“a tree in the fog”** with a confidence score of **73.78%**, alongside tags and a detected tree object. Results vary depending on the image.

## Interface preview

### Image caption and uploaded image

![Uploaded image and caption result](screenshots/image-caption.png)

### Tags, object detection and OCR results

![Detected tags, objects and OCR output](screenshots/analysis-results.png)

## Features

- **Image upload:** Select a supported image through the browser.
- **Image caption:** Displays a generated caption and confidence score when returned by the service.
- **Image tags:** Lists labels describing the image, each with a confidence score.
- **Object detection:** Displays detected object labels, confidence scores and bounding-box coordinates when available.
- **OCR (text recognition):** Displays text lines returned by the image-reading feature.
- **Image preview:** Shows the uploaded image on the results page.
- **API error handling:** Presents useful messages for common authentication, endpoint, request-limit and network errors.
- **Credential separation:** Reads the Azure endpoint and key from environment variables rather than hard-coding them in source code.

## How it works

```text
User selects image
       |
       v
Flask web application
       |
       | HTTPS REST API request
       v
Microsoft Azure AI Vision
       |
       | JSON analysis response
       v
Flask parses response
       |
       v
Caption + tags + objects + OCR displayed in browser
```

The application uses the Azure Image Analysis REST API with the `2024-02-01` API version and requests the `caption`, `tags`, `objects`, and `read` features. Availability can depend on the Azure resource, region, pricing tier, and API support.

## Technology stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Flask | Web server and upload form |
| Requests | HTTPS calls to Azure AI Vision |
| python-dotenv | Load local configuration from `.env` |
| Microsoft Azure AI Vision | Cloud-based image analysis |
| HTML and CSS | User interface and result layout |

## Run locally

### 1. Prerequisites

- Python 3 installed
- A Microsoft Azure subscription with an Azure AI Vision / Computer Vision resource
- The resource endpoint and API key
- Git, if cloning the repository

### 2. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/AzureImageAnalysis.git
cd AzureImageAnalysis
```

Replace `YOUR-USERNAME` with your GitHub username and use the actual repository name if it differs.

### 3. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can allow it for the current terminal session and retry:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create a file named `.env` in the same directory as `app.py`:

```dotenv
VISION_ENDPOINT=https://YOUR-RESOURCE-NAME.cognitiveservices.azure.com
VISION_KEY=YOUR_AZURE_KEY
```

Replace the placeholders with the endpoint and key from your Azure resource's **Keys and Endpoint** page.

### 6. Start the application

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser, select an image, and click **Analyze Image**.

## Configuration and security

- Do **not** commit `.env` or expose your Azure key in screenshots, reports, public issues, or source code.
- Confirm `.env` is excluded in `.gitignore`.
- If a key is accidentally published, rotate it in Azure; removing the file in a later commit does not remove it from Git history.
- Use environment variables or a managed secret store for deployed applications.
- The local Flask development server is for coursework and testing. Do not expose it publicly with debug mode enabled.
- Validate uploaded file content as well as file extensions/MIME types before using this as a production service.

## Project structure

```text
AzureImageAnalysis/
├── app.py                 # Flask application and Azure API integration
├── requirements.txt       # Python dependencies
├── .env                   # Local secrets (not committed)
├── .gitignore             # Excludes secrets and local environment
├── README.md              # Project documentation
├── index.html             # Interactive GitHub Pages project page
└── screenshots/
    ├── image-caption.png
    └── analysis-results.png
```

## Limitations

- AI results are predictions and may be incomplete or incorrect.
- OCR may return no text for images without readable text.
- Supported features and request quotas depend on the Azure service configuration.
- The current application has a 4 MB upload limit.
- The current object presentation shows labels and bounding-box coordinates; it does not draw the boxes over the image.
- `index.html` is a static project showcase. It does **not** run Python or call Azure itself. The Flask app must run separately to analyze new uploads.

## Learning outcomes

This project demonstrates:

1. Provisioning a cloud-based AI service.
2. Configuring access using an endpoint and API key.
3. Sending image data to a cloud REST API.
4. Parsing JSON responses in Python.
5. Presenting computer-vision output in a web application.
6. Managing project dependencies and protecting credentials with Git.

## References

- [Microsoft Azure AI Vision documentation](https://learn.microsoft.com/azure/ai-services/computer-vision/)
- [Azure Image Analysis REST API](https://learn.microsoft.com/rest/api/computervision/image-analysis/analyze)
- [GitHub Pages documentation](https://docs.github.com/pages)

---

<p align="center">Built as a cloud-computing and computer-vision coursework project.</p>
