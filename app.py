from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from converter.file_to_pdf import convert_file

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/api/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "Fayl topilmadi"}), 400

    file = request.files["file"]
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    output_path, filename = convert_file(input_path, OUTPUT_FOLDER)
    if not output_path:
        return jsonify({"error": "Konvertatsiya bajarilmadi"}), 500

    return jsonify({"downloadUrl": f"/download/{filename}"}), 200

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
