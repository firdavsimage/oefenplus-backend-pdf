import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ilovepdf import ILovePdf

app = Flask(__name__)
CORS(app)

PUBLIC_KEY = "project_public_002668c65677139b50439696e90805e5_JO_Lt06e53e5275b342ceea0429acfc79f0d2"
SECRET_KEY = "secret_key_cb327f74110b4e506fec5ac629878293_SkxGg3f96e8bcdd9594d8e575c15d3dab7b99"

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ilovepdf = ILovePdf(PUBLIC_KEY, SECRET_KEY, verify_ssl=True)

@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'Fayl yuborilmadi'}), 400

    task = None
    merged_file_path = os.path.join(OUTPUT_FOLDER, 'output.pdf')
    file_exts = [os.path.splitext(f.filename)[1].lower() for f in files]

    try:
        if all(ext in ['.jpg', '.jpeg', '.png'] for ext in file_exts):
            task = ilovepdf.new_task('imagepdf')
        elif all(ext in ['.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls'] for ext in file_exts):
            task = ilovepdf.new_task('officepdf')
        else:
            return jsonify({'error': 'Faqat rasmlar yoki Office fayllar yuborilishi mumkin'}), 400

        for file in files:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            task.add_file(filepath)

        task.set_output_folder(OUTPUT_FOLDER)
        task.execute()
        task.download()

        for f in os.listdir(OUTPUT_FOLDER):
            if f.endswith('.pdf'):
                merged_file_path = os.path.join(OUTPUT_FOLDER, f)
                break

        return send_file(merged_file_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        for f in os.listdir(UPLOAD_FOLDER):
            os.remove(os.path.join(UPLOAD_FOLDER, f))
        for f in os.listdir(OUTPUT_FOLDER):
            os.remove(os.path.join(OUTPUT_FOLDER, f))

@app.route('/')
def index():
    return '✅ ILovePDF API Flask Backend is running!'
