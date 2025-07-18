from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from ilovepdf import ILovePdf
import os
import tempfile
# from dotenv import load_dotenv

# load_dotenv()

app = Flask(__name__)
CORS(app)

ILOVEPDF_SECRET = "secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d"

@app.route("/convert", methods=["POST"])
def convert_files():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "Fayl yuborilmadi."}), 400

    try:
        ilovepdf = ILovePdf(ILOVEPDF_SECRET, verify_ssl=True)

        ext = os.path.splitext(files[0].filename)[1].lower()
        if ext in [".jpg", ".jpeg", ".png"]:
            task = ilovepdf.new_task("imagepdf")
        else:
            task = ilovepdf.new_task("officepdf")

        temp_files = []
        for f in files:
            ext = os.path.splitext(f.filename)[1]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            f.save(tmp.name)
            task.add_file(tmp.name)
            temp_files.append(tmp.name)

        task.process()

        result = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        task.download(result.name)

        for f in temp_files:
            os.remove(f)

        return send_file(result.name, as_attachment=True, download_name="output.pdf")

    except Exception as e:
        print("Xatolik:", str(e))
        return jsonify({"error": str(e)}), 500
