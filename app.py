from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import os, uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/api/convert-images', methods=['POST'])
def convert_images_to_pdf():
    if 'files' not in request.files:
        return jsonify({'error': 'Fayllar yuborilmadi'}), 400

    files = request.files.getlist('files')
    images = []

    for file in files:
        img = Image.open(file.stream).convert('RGB')
        images.append(img)

    if not images:
        return jsonify({'error': 'Rasmlar topilmadi'}), 400

    output_filename = f"{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # ✅ 300 DPI bilan PDFga saqlash, rasm kesilmaydi, sifat yuqori
    images[0].save(output_path, save_all=True, append_images=images[1:], resolution=300)

    return jsonify({'downloadUrl': f'/download/{output_filename}'})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
