from flask import Flask, request, send_file, render_template_string
from fpdf import FPDF
from PIL import Image
from docx import Document
from docx2pdf import convert
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
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
        pdf.add_page()
        pdf.image(img, x=10, y=10, w=pdf.w - 20)
    pdf.output(output_path)

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML)

@app.route('/convert', methods=['POST'])
def convert_files():
    pdf_files = []
    # Images -> PDF
    images = request.files.getlist('images')
    image_paths = []
    for img in images:
        filename = secure_filename(img.filename)
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(img_path)
        image_paths.append(img_path)
    if image_paths:
        img_pdf = os.path.join(app.config['UPLOAD_FOLDER'], 'images.pdf')
        images_to_pdf(image_paths, img_pdf)
        pdf_files.append(img_pdf)

    # PPT -> PDF (first, convert to pptx images, then images to pdf)
    ppt_file = request.files.get('ppt')
    if ppt_file:
        pptx_filename = secure_filename(ppt_file.filename)
        pptx_path = os.path.join(app.config['UPLOAD_FOLDER'], pptx_filename)
        ppt_file.save(pptx_path)
        # Render pptx slides as images
        from pptx import Presentation
        ppt = Presentation(pptx_path)
        slide_imgs = []
        for i, slide in enumerate(ppt.slides):
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], f'slide_{i + 1}.png')
            slide_imgs.append(img_path)
            # Save blank image (for demo), you can use python-pptx-to-image libraries for real rendering
            img = Image.new('RGB', (1280, 720), color='white')
            img.save(img_path)
        ppt_pdf = os.path.join(app.config['UPLOAD_FOLDER'], 'ppt.pdf')
        images_to_pdf(slide_imgs, ppt_pdf)
        pdf_files.append(ppt_pdf)

    # Word -> PDF
    word_file = request.files.get('word')
    if word_file:
        word_filename = secure_filename(word_file.filename)
        word_path = os.path.join(app.config['UPLOAD_FOLDER'], word_filename)
        word_file.save(word_path)
        word_pdf = os.path.join(app.config['UPLOAD_FOLDER'], 'word.pdf')
        convert(word_path, word_pdf)
        pdf_files.append(word_pdf)

    # If multiple PDFs, zip them
    if len(pdf_files) == 1:
        return send_file(pdf_files[0], as_attachment=True)
    else:
        import zipfile
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted_files.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf in pdf_files:
                zipf.write(pdf, os.path.basename(pdf))
        return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
