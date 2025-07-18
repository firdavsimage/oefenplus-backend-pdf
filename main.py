import os
import requests
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from tempfile import NamedTemporaryFile

app = Flask(__name__)
CORS(app)

ILOVEPDF_SECRET = "secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d"

@app.route("/convert", methods=["POST"])
def convert_files():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    # 1. Yangi task yaratamiz
    task = requests.post(
        "https://api.ilovepdf.com/v1/start/all",
        json={"public_key": ILOVEPDF_SECRET}
    ).json()
    server = task["server"]
    task_id = task["task"]

    # 2. Har bir faylni upload qilamiz
    for file in files:
        file_upload = requests.post(
            f"https://{server}/v1/upload",
            files={"file": (file.filename, file.stream)},
            data={"task": task_id}
        ).json()
    
    # 3. Fayllarni PDF qilib birlashtiramiz
    process = requests.post(
        f"https://{server}/v1/process",
        json={
            "task": task_id,
            "tool": "all",
            "output_filename": "converted.pdf"
        }
    ).json()

    # 4. Tayyor faylni yuklab olamiz
    result = requests.get(
        f"https://{server}/v1/download/{task_id}",
        stream=True
    )

    # 5. Mahalliyga vaqtincha saqlaymiz
    temp_file = NamedTemporaryFile(delete=False, suffix=".pdf")
    for chunk in result.iter_content(chunk_size=8192):
        temp_file.write(chunk)
    temp_file.close()

    return send_file(temp_file.name, as_attachment=True, download_name="converted.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
