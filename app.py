from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import os, uuid
from converter import convert_docx, convert_pptx, convert_xlsx

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/api/convert-file', methods=['POST'])
def convert_file_to_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'Fayl yuborilmadi'}), 400

    file = request.files['file']
    filename = file.filename
    ext = filename.rsplit('.', 1)[-1].lower()

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        if ext == 'docx':
            output_path = convert_docx(input_path, OUTPUT_FOLDER)
        elif ext == 'pptx':
            output_path = convert_pptx(input_path, OUTPUT_FOLDER)
        elif ext == 'xlsx':
            output_path = convert_xlsx(input_path, OUTPUT_FOLDER)
        else:
            return jsonify({'error': 'Fayl turi qo‘llab-quvvatlanmaydi'}), 400
    except Exception as e:
        return jsonify({'error': f'Xatolik: {str(e)}'}), 500

    filename_out = os.path.basename(output_path)
    return jsonify({'downloadUrl': f'/download/{filename_out}'})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
