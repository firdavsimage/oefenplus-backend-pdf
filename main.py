from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import hashlib
import uuid
import requests
from flask_cors import CORS  # ✅ CORS import qilindi

app = Flask(__name__)
CORS(app, origins=["https://oefenplus.uz"])  # ✅ Faqat shu frontend domeniga ruxsat berildi

UPLOAD_FOLDER = "uploads"
CACHE_FOLDER = "cache"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CACHE_FOLDER, exist_ok=True)

ILOVEPDF_SECRET = "secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d"

def file_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

@app.route("/convert", methods=["POST"])
def convert_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Fayl yuborilmadi"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower()

    if ext not in ['jpg', 'jpeg', 'png', 'docx', 'pptx']:
        return jsonify({"error": "Yaroqsiz fayl turi"}), 400

    uid = uuid.uuid4().hex
    filepath = os.path.join(UPLOAD_FOLDER, f"{uid}_{filename}")
    file.save(filepath)

    hashname = file_hash(filepath)
    cached_pdf = os.path.join(CACHE_FOLDER, f"{hashname}.pdf")
    if os.path.exists(cached_pdf):
        return send_file(cached_pdf, as_attachment=True)

    # API: iLovePDF
    try:
        # 1. Task yaratish
        res = requests.post("https://api.ilovepdf.com/v1/start/convert", json={
            "public_key": ILOVEPDF_SECRET,
            "task": "officepdf" if ext in ["docx", "pptx"] else "imagepdf"
        })
        task = res.json()
        server = task["server"]
        task_id = task["task"]

        # 2. Fayl yuklash
        with open(filepath, "rb") as f:
            requests.post(f"https://{server}/v1/upload", files={
                'file': (filename, f)
            }, data={
                'task': task_id
            })

        # 3. Konvertatsiya qilish
        requests.post(f"https://{server}/v1/process", data={
            "task": task_id
        })

        # 4. Yuklab olish
        output = requests.get(f"https://{server}/v1/download/{task_id}", stream=True)
        with open(cached_pdf, 'wb') as f:
            for chunk in output.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return send_file(cached_pdf, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
