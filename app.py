
import os
import base64
import requests

from flask import Flask, request, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024  # 4 MB

VISION_ENDPOINT = os.getenv("VISION_ENDPOINT", "").rstrip("/")
VISION_KEY = os.getenv("VISION_KEY", "")

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/bmp",
}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Azure Image Analysis</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f2f5fa;
            margin: 0;
            padding: 35px 16px;
            color: #202938;
        }
        main {
            max-width: 850px;
            margin: auto;
            background: white;
            padding: 28px;
            border-radius: 14px;
            box-shadow: 0 4px 18px #00000012;
        }
        h1 { color: #1769aa; }
        .hint { color: #596579; }
        input, button {
            padding: 12px;
            margin: 8px 0;
        }
        button {
            background: #1769aa;
            color: white;
            border: 0;
            border-radius: 6px;
            cursor: pointer;
        }
        button:hover { background: #104c80; }
        .panel {
            background: #f5f8fc;
            padding: 16px;
            border-radius: 9px;
            margin-top: 18px;
            overflow-wrap: anywhere;
        }
        .preview {
            display: block;
            max-width: 100%;
            max-height: 380px;
            margin-top: 14px;
            border-radius: 8px;
        }
        li { margin: 9px 0; }
        .error { color: #b42318; }
        code { overflow-wrap: anywhere; }
    </style>
</head>
<body>
<main>
    <h1>Cloud-Based Image Analysis</h1>
    <p class="hint">
        Upload an image to detect its caption, tags, objects and text
        using Microsoft Azure AI Vision.
    </p>

    <form method="POST" enctype="multipart/form-data">
        <label for="image"><b>Select an image</b></label><br>
        <input id="image" type="file" name="image"
               accept="image/jpeg,image/png,image/gif,image/bmp"
               required><br>
        <button type="submit">Analyze Image</button>
    </form>

    {% if error %}
        <div class="panel error">
            <b>Analysis failed:</b> {{ error }}
        </div>
    {% endif %}

    {% if preview %}
        <div class="panel">
            <h2>Uploaded Image</h2>
            <img class="preview"
                 src="data:{{ mime }};base64,{{ preview }}"
                 alt="Uploaded image">
        </div>
    {% endif %}

    {% if result %}
        <div class="panel">
            <h2>Image Caption</h2>
            {% if caption %}
                <p>{{ caption }}</p>
                <p>Confidence: {{ "%.2f"|format(caption_conf * 100) }}%</p>
            {% else %}
                <p>No caption was returned.</p>
            {% endif %}
        </div>

        <div class="panel">
            <h2>Detected Tags</h2>
            {% if tags %}
                <ul>
                {% for tag in tags %}
                    <li>{{ tag.name }} —
                        {{ "%.2f"|format(tag.confidence * 100) }}%
                        confidence
                    </li>
                {% endfor %}
                </ul>
            {% else %}
                <p>No tags were returned.</p>
            {% endif %}
        </div>

        <div class="panel">
            <h2>Detected Objects</h2>
            {% if objects %}
                <ul>
                {% for obj in objects %}
                    <li>
                        {{ obj.name }} —
                        {{ "%.2f"|format(obj.confidence * 100) }}%
                        confidence
                        {% if obj.box %}
                            <br><small>Bounding box: {{ obj.box }}</small>
                        {% endif %}
                    </li>
                {% endfor %}
                </ul>
            {% else %}
                <p>No objects were returned.</p>
            {% endif %}
        </div>

        <div class="panel">
            <h2>Text Detected (OCR)</h2>
            {% if text_lines %}
                <ul>
                {% for line in text_lines %}
                    <li>{{ line }}</li>
                {% endfor %}
                </ul>
            {% else %}
                <p>No readable text was detected.</p>
            {% endif %}
        </div>
    {% endif %}
</main>
</body>
</html>
"""


def analyze_image(image_bytes):
    if not VISION_ENDPOINT or not VISION_KEY:
        raise RuntimeError(
            "Missing VISION_ENDPOINT or VISION_KEY in your .env file."
        )

    url = (
        f"{VISION_ENDPOINT}/computervision/"
        "imageanalysis:analyze"
    )

    params = {
        "api-version": "2024-02-01",
        "features": "caption,tags,objects,read",
    }

    headers = {
        "Ocp-Apim-Subscription-Key": VISION_KEY,
        "Content-Type": "application/octet-stream",
    }

    response = requests.post(
        url,
        params=params,
        headers=headers,
        data=image_bytes,
        timeout=60,
    )

    if not response.ok:
        if response.status_code == 401:
            raise RuntimeError(
                "Azure authentication failed. Check your API key."
            )
        if response.status_code == 404:
            raise RuntimeError(
                "Endpoint or API route not found. Check your Azure "
                "resource endpoint and supported API version."
            )
        if response.status_code == 429:
            raise RuntimeError(
                "Azure request limit reached. Wait and try again."
            )

        raise RuntimeError(
            f"Azure returned HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    return response.json()


@app.route("/", methods=["GET", "POST"])
def home():
    error = None
    result = None
    preview = None
    mime = None
    caption = None
    caption_conf = 0.0
    tags = []
    objects = []
    text_lines = []

    if request.method == "POST":
        uploaded = request.files.get("image")

        if not uploaded or not uploaded.filename:
            error = "Please select an image first."

        elif uploaded.mimetype not in ALLOWED_TYPES:
            error = "Upload a JPG, PNG, GIF or BMP image."

        else:
            image_bytes = uploaded.read()

            if not image_bytes:
                error = "The uploaded file is empty."

            elif len(image_bytes) > 4 * 1024 * 1024:
                error = "The image must be smaller than 4 MB."

            else:
                mime = uploaded.mimetype
                preview = base64.b64encode(
                    image_bytes
                ).decode("utf-8")

                try:
                    result = analyze_image(image_bytes)

                    caption_data = result.get("captionResult") or {}
                    caption = caption_data.get("text")
                    caption_conf = caption_data.get(
                        "confidence", 0.0
                    )

                    tags = (result.get("tagsResult") or {}).get(
                        "values", []
                    )

                    for item in (
                        result.get("objectsResult") or {}
                    ).get("values", []):
                        names = item.get("tags", [])
                        box = item.get("boundingBox")

                        for tag in names:
                            objects.append({
                                "name": tag.get("name", "Unknown"),
                                "confidence": tag.get(
                                    "confidence", 0.0
                                ),
                                "box": box,
                            })

                    read_result = result.get("readResult") or {}
                    for block in read_result.get("blocks", []):
                        for line in block.get("lines", []):
                            if line.get("text"):
                                text_lines.append(line["text"])

                except requests.Timeout:
                    error = "Azure took too long to respond. Try again."
                    result = None

                except requests.RequestException as exc:
                    error = f"Network request failed: {exc}"
                    result = None

                except (RuntimeError, ValueError) as exc:
                    error = str(exc)
                    result = None

    return render_template_string(
        HTML,
        error=error,
        result=result,
        preview=preview,
        mime=mime,
        caption=caption,
        caption_conf=caption_conf,
        tags=tags,
        objects=objects,
        text_lines=text_lines,
    )


@app.errorhandler(413)
def file_too_large(error):
    return (
        "The uploaded image is too large. Maximum size is 4 MB.",
        413,
    )


if __name__ == "__main__":
    app.run(debug=True)
