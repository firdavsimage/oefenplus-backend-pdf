from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from pylovepdf.ilovepdf import ILovePdf
import os
import uuid
import shutil

app = Flask(__name__)
CORS(app, origins=["https://oefenplus.uz"])

# API kalitlari va papkalar
ILOVEPDF_PUBLIC_KEY = "project_public_002668c65677139b50439696e90805e5_JO_Lt06e53e5275b342ceea0429acfc79f0d2"
UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/api/convert', methods=['POST'])
def convert_to_pdf():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "Hech qanday fayl yuborilmadi."}), 400

    # Task ID bilan har bir foydalanuvchi uchun alohida katalog yaratamiz
    task_id = str(uuid.uuid4())
    user_folder = os.path.join(UPLOAD_FOLDER, task_id)
    os.makedirs(user_folder, exist_ok=True)

    try:
        ilovepdf = ILovePdf(ILOVEPDF_PUBLIC_KEY, verify_ssl=True)
        task = ilovepdf.new_task('officepdf')

        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(user_folder, filename)
            file.save(filepath)
            task.add_file(filepath)

        task.set_output_folder(RESULT_FOLDER)
        task.execute()
        task.download()
        task.delete_current_task()

        # PDF yoki ZIP natijani topish
        result_file = None
        for f in os.listdir(RESULT_FOLDER):
            if f.endswith('.pdf') or f.endswith('.zip'):
                result_file = f
                break

        if not result_file:
            return jsonify({"error": "PDF fayl topilmadi"}), 500

        return jsonify({
            "download_url": f"/download/{result_file}"
        })

    except Exception as e:
        print("Xatolik:", e)
        return jsonify({"error": "Konvertatsiya xatoligi: " + str(e)}), 500

    finally:
        # Kiritilgan fayllarni tozalaymiz
        shutil.rmtree(user_folder, ignore_errors=True)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
