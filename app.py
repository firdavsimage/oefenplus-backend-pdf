from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pylovepdf.ilovepdf import ILovePdf
import os
import uuid

app = Flask(__name__)
CORS(app, origins=["https://oefenplus.uz"])

# Konfiguratsiya
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

    # ILovePDF klientini ishga tushirish
    ilovepdf = ILovePdf(ILOVEPDF_PUBLIC_KEY, verify_ssl=True)
    task = ilovepdf.new_task('officepdf')  # DOC, XLS, PPT, Images...

    try:
        for file in files:
            filename = secure_filename(file.filename)
            task.add_file(file.stream, filename=filename)

        task.set_output_folder(RESULT_FOLDER)
        task.execute()
        task.download()
        task.delete_current_task()

        # Natijaviy faylni topamiz (zip yoki pdf)
        for fname in os.listdir(RESULT_FOLDER):
            if fname.endswith(".pdf") or fname.endswith(".zip"):
                result_filename = fname
                break
        else:
            return jsonify({"error": "PDF fayl topilmadi"}), 500

        return jsonify({
            "download_url": f"/download/{result_filename}"
        })

    except Exception as e:
        print("Xatolik:", e)
        return jsonify({"error": "Konvertatsiyada xatolik yuz berdi."}), 500


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
