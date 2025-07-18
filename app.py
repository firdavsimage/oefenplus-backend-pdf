import os
import tempfile
from flask import Flask, request, jsonify
from pylovepdf import ILovePdf

app = Flask(__name__)

# API kalitlari
PUBLIC_KEY = 'project_public_002668c65677139b50439696e90805e5_JO_Lt06e53e5275b342ceea0429acfc79f0d2'
SECRET_KEY = 'secret_key_cb327f74110b4e506fec5ac629878293_SkxGg3f96e8bcdd9594d8e575c15d3dab7b99'

@app.route('/api/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Fayl topilmadi'}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'error': 'Fayl tanlanmadi'}), 400

    # Faylni vaqtincha saqlash
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.filename)
    uploaded_file.save(file_path)

    try:
        ilovepdf = ILovePdf(PUBLIC_KEY, verify_ssl=True)
        task = ilovepdf.new_task('officepdf')  # Word, PPT, Excel uchun mos

        task.add_file(file_path)
        task.set_output_folder(temp_dir)
        task.execute()
        task.download()

        # Topilgan yagona PDF fayl
        pdf_file = next((f for f in os.listdir(temp_dir) if f.endswith('.pdf')), None)
        if pdf_file:
            return jsonify({'download_url': f'/download/{pdf_file}'})
        else:
            return jsonify({'error': 'PDF yaratib bo‘lmadi'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    from flask import send_from_directory
    temp_dir = tempfile.gettempdir()
    return send_from_directory(temp_dir, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
