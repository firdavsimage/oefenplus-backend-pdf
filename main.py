from flask import Flask, request, send_file
from flask_cors import CORS
import requests
import os
from tempfile import NamedTemporaryFile

app = Flask(__name__)
CORS(app)  # CORS yoqildi — barcha domenlarga ruxsat

ILOVEPDF_SECRET = "secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d"

@app.route("/convert", methods=["POST"])
def convert():
    files = request.files.getlist("files")
    if not files:
        return {"error": "No files uploaded"}, 400

    # Fayllarni vaqtinchalik saqlash
    temp_files = []
    for file in files:
        temp = NamedTemporaryFile(delete=False)
        file.save(temp.name)
        temp_files.append(temp)

    try:
        # ilovepdf APIga ulanish
        response = requests.post(
            "https://api.ilovepdf.com/v1/start/merge",
            headers={"Authorization": f"Bearer {ILOVEPDF_SECRET}"}
        )
        task = response.json()
        server = task["server"]
        task_id = task["task"]

        # Fayllarni yuklash
        for temp in temp_files:
            with open(temp.name, "rb") as f:
                requests.post(
                    f"https://{server}/v1/upload",
                    params={"task": task_id},
                    files={"file": f}
                )

        # Birlash va yuklab olish
        requests.post(f"https://{server}/v1/process", params={"task": task_id})
        download = requests.get(f"https://{server}/v1/download", params={"task": task_id}, stream=True)

        out = NamedTemporaryFile(delete=False, suffix=".pdf")
        for chunk in download.iter_content(chunk_size=8192):
            out.write(chunk)
        out.seek(0)

        return send_file(out.name, as_attachment=True, download_name="converted.pdf", mimetype="application/pdf")

    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        for temp in temp_files:
            os.unlink(temp.name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
