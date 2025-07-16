from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from file_to_pdf import convert_file

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/api/convert-file', methods=['POST'])
def convert_to_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'Fayl topilmadi'}), 400

    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    try:
        output_path = convert_file(input_path, OUTPUT_FOLDER)
    except Exception as e:
        return jsonify({'error': f'Xatolik: {str(e)}'}), 500

    return jsonify({'downloadUrl': f'/download/{os.path.basename(output_path)}'})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
