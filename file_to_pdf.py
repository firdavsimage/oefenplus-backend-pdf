import os
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape, portrait
from PIL import Image
import uuid
from PyPDF2 import PdfMerger

def convert_files(input_paths, output_path):
    try:
        temp_pdf_files = []

        for path in input_paths:
            ext = os.path.splitext(path)[1].lower()

            if ext in ['.jpg', '.jpeg', '.png']:
                temp_pdf = f"converted/{uuid.uuid4().hex}.pdf"
                if convert_image_to_pdf(path, temp_pdf):
                    temp_pdf_files.append(temp_pdf)
            elif ext in ['.docx', '.pptx', '.xlsx']:
                result = subprocess.run([
                    'libreoffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', 'converted',
                    path
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if result.returncode == 0:
                    base_name = os.path.splitext(os.path.basename(path))[0]
                    temp_pdf = os.path.join('converted', base_name + '.pdf')
                    if os.path.exists(temp_pdf):
                        temp_pdf_files.append(temp_pdf)
                else:
                    print(f"[XATO] LibreOffice bilan konvertatsiyada muammo: {result.stderr.decode()}")

        if len(temp_pdf_files) == 1:
            os.rename(temp_pdf_files[0], output_path)
        elif len(temp_pdf_files) > 1:
            merger = PdfMerger()
            for pdf in temp_pdf_files:
                merger.append(pdf)
            merger.write(output_path)
            merger.close()
            for pdf in temp_pdf_files:
                os.remove(pdf)

        return True
    except Exception as e:
        print(f"[XATO] Konvertatsiyada xatolik: {e}")
        return False
    finally:
        for path in input_paths:
            try:
                os.remove(path)
            except Exception:
                pass

def convert_image_to_pdf(image_path, pdf_path):
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        img_width, img_height = img.size

        if img_width > img_height:
            page_size = landscape(A4)
        else:
            page_size = portrait(A4)

        page_width, page_height = page_size
        ratio = min(page_width / img_width, page_height / img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2

        c = canvas.Canvas(pdf_path, pagesize=page_size)
        img.save("temp_image.jpg", dpi=(300, 300))
        c.drawImage("temp_image.jpg", x, y, width=new_width, height=new_height)
        c.showPage()
        c.save()
        os.remove("temp_image.jpg")

        return True
    except Exception as e:
        print(f"[XATO] Rasmni PDF-ga o‘tkazishda xatolik: {e}")
        return False
