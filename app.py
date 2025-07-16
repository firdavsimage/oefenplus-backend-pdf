import os
from docx import Document
from pptx import Presentation
from openpyxl import load_workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image

def convert_file(filepath, output_folder):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.docx':
        return convert_docx(filepath, output_folder)
    elif ext == '.pptx':
        return convert_pptx(filepath, output_folder)
    elif ext == '.xlsx':
        return convert_xlsx(filepath, output_folder)
    elif ext in ['.jpg', '.jpeg', '.png']:
        return convert_images([filepath], output_folder)
    else:
        return None, None

def convert_docx(file_path, output_folder):
    doc = Document(file_path)
    output_pdf = os.path.join(output_folder, os.path.splitext(os.path.basename(file_path))[0] + ".pdf")
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4
    y = height - 50

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            c.drawString(50, y, text)
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50

    c.save()
    return output_pdf, os.path.basename(output_pdf)

def convert_pptx(file_path, output_folder):
    prs = Presentation(file_path)
    output_pdf = os.path.join(output_folder, os.path.splitext(os.path.basename(file_path))[0] + ".pdf")
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4

    for slide in prs.slides:
        y = height - 50
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                lines = shape.text.split('\n')
                for line in lines:
                    c.drawString(50, y, line.strip())
                    y -= 20
                    if y < 50:
                        c.showPage()
                        y = height - 50
        c.showPage()

    c.save()
    return output_pdf, os.path.basename(output_pdf)

def convert_xlsx(file_path, output_folder):
    wb = load_workbook(file_path)
    output_pdf = os.path.join(output_folder, os.path.splitext(os.path.basename(file_path))[0] + ".pdf")
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4
    y = height - 50

    for sheet in wb.worksheets:
        for row in sheet.iter_rows(values_only=True):
            line = ' | '.join([str(cell) if cell is not None else '' for cell in row])
            c.drawString(50, y, line)
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50
        c.showPage()

    c.save()
    return output_pdf, os.path.basename(output_pdf)

def convert_images(image_paths, output_folder):
    output_pdf = os.path.join(output_folder, "converted_images.pdf")
    image_list = []

    for img_path in image_paths:
        img = Image.open(img_path)
        img = img.convert("RGB")
        image_list.append(img)

    if image_list:
        image_list[0].save(output_pdf, save_all=True, append_images=image_list[1:], resolution=300)
        return output_pdf, os.path.basename(output_pdf)

    return None, None
