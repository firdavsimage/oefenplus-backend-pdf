from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import shutil
from file_to_pdf import convert_files

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/api/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'Fayl yuborilmadi'}), 400

    files = request.files.getlist('file')
    saved_paths = []

    for file in files:
        file_id = uuid.uuid4().hex
        file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{file.filename}")
        file.save(file_path)
        saved_paths.append(file_path)

    output_filename = f"{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    success = convert_files(saved_paths, output_path)

    # Keshni tozalash
    for path in saved_paths:
        os.remove(path)

    if success:
        return jsonify({'downloadUrl': f'/download/{output_filename}'})
    else:
        return jsonify({'error': 'Konvertatsiya qilishda xatolik'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
