import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ILOVEPDF_SECRET = "secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d"

@app.route("/convert", methods=["POST"])
def convert_files():
    try:
        files = request.files.getlist("files")
        if not files:
            return jsonify({"error": "No files uploaded"}), 400

        task_response = requests.post(
            "https://api.ilovepdf.com/v1/start/all",
            json={"public_key": ILOVEPDF_SECRET}
        )
        print("TASK RESPONSE:", task_response.text)

        task = task_response.json()
        server = task["server"]
        task_id = task["task"]

        for file in files:
            upload_response = requests.post(
                f"https://{server}/v1/upload",
                files={"file": (file.filename, file.stream)},
                data={"task": task_id}
            )
            print(f"UPLOAD RESPONSE for {file.filename}:", upload_response.text)

        process_response = requests.post(
            f"https://{server}/v1/process",
            json={
                "task": task_id,
                "tool": "all",
                "output_filename": "converted.pdf"
            }
        )
        print("PROCESS RESPONSE:", process_response.text)

        download_url = f"https://{server}/v1/download/{task_id}"
        return jsonify({"url": download_url})

    except Exception as e:
        print("SERVER ERROR:", str(e))
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
