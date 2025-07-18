from flask import Flask, request, send_file
import requests, time, os

app = Flask(__name__)

API_KEY = "secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d"

@app.route("/convert", methods=["POST"])
def convert_to_pdf():
    files = request.files.getlist("files")
    if not files:
        return {"error": "Hech qanday fayl yuborilmadi"}, 400

    # 1. Start task
    tool_type = detect_tool(files[0].filename)
    start_res = requests.post(
        f"https://api.ilovepdf.com/v1/start/{tool_type}",
        headers={"Authorization": f"Bearer {API_KEY}"}
    ).json()
    task = start_res["task"]

    # 2. Upload files
    uploaded = []
    for file in files:
        local_path = f"/tmp/{file.filename}"
        file.save(local_path)
        with open(local_path, "rb") as f:
            upload_res = requests.post(
                "https://api.ilovepdf.com/v1/upload",
                params={"task": task},
                files={"file": (file.filename, f)}
            ).json()
            uploaded.append(upload_res)

    # 3. Process
    process_res = requests.post(
        "https://api.ilovepdf.com/v1/process",
        data={"task": task}
    ).json()

    # 4. Download result
    download = requests.get(
        "https://api.ilovepdf.com/v1/download",
        params={"task": task},
        stream=True
    )

    output = f"/tmp/result_{int(time.time())}.pdf"
    with open(output, "wb") as f:
        for chunk in download.iter_content(chunk_size=8192):
            f.write(chunk)

    return send_file(output, as_attachment=True, download_name="converted.pdf", mimetype="application/pdf")

def detect_tool(filename):
    ext = filename.lower().split('.')[-1]
    if ext in ["jpg", "jpeg", "png"]:
        return "imagepdf"
    if ext in ["doc", "docx"]:
        return "officepdf"
    if ext in ["ppt", "pptx"]:
        return "officepdf"
    return "imagepdf"  # fallback

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
