from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from file_to_pdf import convert_file

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route('/api/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'Fayl yuborilmadi'}), 400

    file = request.files['file']
    saved_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(saved_path)

    output_path, filename = convert_file(saved_path, CONVERTED_FOLDER)
    if not output_path:
        return jsonify({'error': 'Faylni konvertatsiya qilishda xatolik'}), 500

    return jsonify({'downloadUrl': f'/download/{filename}'})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(CONVERTED_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
