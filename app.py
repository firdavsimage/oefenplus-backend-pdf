# app.py
import os
import shutil
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from converter.image_converter import convert_image_to_pdf
from converter.docx_converter import convert_docx_to_pdf
from converter.pptx_converter import convert_pptx_to_pdf
from converter.excel_converter import convert_excel_to_pdf

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'docx', 'pptx', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400

    ext = files[0].filename.rsplit('.', 1)[1].lower()
    output_filename = 'converted.pdf'
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    try:
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(input_path)
            else:
                return jsonify({'error': 'Invalid file'}), 400

        if ext in ['jpg', 'jpeg', 'png']:
            convert_image_to_pdf(app.config['UPLOAD_FOLDER'], output_path)
        elif ext == 'docx':
            convert_docx_to_pdf(input_path, output_path)
        elif ext == 'pptx':
            convert_pptx_to_pdf(input_path, output_path)
        elif ext == 'xlsx':
            convert_excel_to_pdf(input_path, output_path)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400

        return send_file(output_path, as_attachment=True)
    finally:
        shutil.rmtree(UPLOAD_FOLDER)
        shutil.rmtree(OUTPUT_FOLDER)
        os.makedirs(UPLOAD_FOLDER)
        os.makedirs(OUTPUT_FOLDER)

    else:
        return jsonify({'error': 'Invalid file'}), 400

if __name__ == '__main__':
    app.run(debug=True)
