from flask import Flask, request, send_file, render_template_string
from fpdf import FPDF
from PIL import Image
import os
from werkzeug.utils import secure_filename
import subprocess
import zipfile
import hashlib
from flask_cors import CORS  # ⬅️ YANGI

app = Flask(__name__)
CORS(app)  # ⬅️ CORS ni shu yerga qo‘shamiz

@app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200


UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

HTML = """
<!DOCTYPE html>
<html>
<head><title>File to PDF Converter</title></head>
<body>
<h2>Convert Images, PPT, Word to PDF</h2>
<form action="/convert" method="post" enctype="multipart/form-data">
    <label>Select images for PDF:</label>
    <input type="file" name="images" multiple><br><br>
    <label>Upload PPT file (.pptx):</label>
    <input type="file" name="ppt"><br><br>
    <label>Upload Word file (.docx):</label>
    <input type="file" name="word"><br><br>
    <input type="submit" value="Convert">
</form>
</body>
</html>
"""

def images_to_pdf(images, output_path):
    pdf = FPDF()
    for img in images:
        image = Image.open(img)
        width, height = image.size
        orientation = 'L' if width > height else 'P'
        pdf.add_page(orientation=orientation)
        page_w = pdf.w - 20
        page_h = pdf.h - 20
        ratio = min(page_w / width, page_h / height)
        new_w = int(width * ratio)
        new_h = int(height * ratio)
        pdf.image(img, x=10, y=10, w=new_w, h=new_h)
    pdf.output(output_path)

def get_file_hash(file_path):
    h = hashlib.md5()
    with open(file_path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def check_cached_pdf(input_path, out_dir):
    file_hash = get_file_hash(input_path)
    cached_pdf = os.path.join(out_dir, f"{file_hash}.pdf")
    if os.path.exists(cached_pdf):
        return cached_pdf
    return None

def libreoffice_convert(input_path, output_dir):
    cmd = [
        "soffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_path
    ]
    subprocess.run(cmd, check=True)
    output_pdf = os.path.join(
        output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    )
    return output_pdf

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)

@app.route("/convert", methods=["POST"])
def convert_files():
    pdf_files = []

    # Images
    images = request.files.getlist('images')
    image_paths = []
    for img in images:
        if img.filename:
            filename = secure_filename(img.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(img_path)
            image_paths.append(img_path)
    if image_paths:
        img_pdf = os.path.join(app.config['UPLOAD_FOLDER'], 'images.pdf')
        images_to_pdf(image_paths, img_pdf)
        pdf_files.append(img_pdf)

    # PPT
    ppt_file = request.files.get('ppt')
    if ppt_file and ppt_file.filename:
        pptx_filename = secure_filename(ppt_file.filename)
        pptx_path = os.path.join(app.config['UPLOAD_FOLDER'], pptx_filename)
        ppt_file.save(pptx_path)
        cached_pdf = check_cached_pdf(pptx_path, app.config['UPLOAD_FOLDER'])
        if cached_pdf:
            pdf_files.append(cached_pdf)
        else:
            ppt_pdf = libreoffice_convert(pptx_path, app.config['UPLOAD_FOLDER'])
            file_hash = get_file_hash(pptx_path)
            cached_pdf = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_hash}.pdf")
            os.rename(ppt_pdf, cached_pdf)
            pdf_files.append(cached_pdf)

    # Word
    word_file = request.files.get('word')
    if word_file and word_file.filename:
        word_filename = secure_filename(word_file.filename)
        word_path = os.path.join(app.config['UPLOAD_FOLDER'], word_filename)
        word_file.save(word_path)
        cached_pdf = check_cached_pdf(word_path, app.config['UPLOAD_FOLDER'])
        if cached_pdf:
            pdf_files.append(cached_pdf)
        else:
            word_pdf = libreoffice_convert(word_path, app.config['UPLOAD_FOLDER'])
            file_hash = get_file_hash(word_path)
            cached_pdf = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_hash}.pdf")
            os.rename(word_pdf, cached_pdf)
            pdf_files.append(cached_pdf)

    # Return response
    if len(pdf_files) == 1:
        return send_file(pdf_files[0], as_attachment=True)
    elif len(pdf_files) > 1:
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted_files.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf in pdf_files:
                zipf.write(pdf, os.path.basename(pdf))
        return send_file(zip_path, as_attachment=True)
    else:
        return "No files uploaded or converted.", 400

@app.route("/soffice-check")
def soffice_check():
    try:
        result = subprocess.run(
            ["soffice", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout or result.stderr
        return f"<pre>{output}</pre>"
    except FileNotFoundError:
        return "❌ soffice (LibreOffice) o‘rnatilmagan"

if __name__ == '__main__':
    app.run(debug=True)
