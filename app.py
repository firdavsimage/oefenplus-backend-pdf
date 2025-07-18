import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

ILOVEPDF_SECRET = "secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d"

@app.route("/convert", methods=["POST"])
def convert_files():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    task = requests.post("https://api.ilovepdf.com/v1/start/all", json={"public_key": ILOVEPDF_SECRET}).json()
    server = task["server"]
    task_id = task["task"]

    for file in files:
        requests.post(
            f"https://{server}/v1/upload",
            files={"file": (file.filename, file.stream)},
            data={"task": task_id}
        )

    requests.post(
        f"https://{server}/v1/process",
        json={"task": task_id, "tool": "all", "output_filename": "converted.pdf"}
    )

    # 3. PDF fayl havolasi
    download_url = f"https://{server}/v1/download/{task_id}"
    return jsonify({"url": download_url})
