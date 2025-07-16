import os
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import uuid

def convert_files(input_paths, output_path):
    try:
        temp_pdf_files = []

        for path in input_paths:
            ext = os.path.splitext(path)[1].lower()

            if ext in ['.jpg', '.jpeg', '.png']:
                # Rasmni PDF-ga aylantirish
                temp_pdf = f"converted/{uuid.uuid4().hex}.pdf"
                if convert_image_to_pdf(path, temp_pdf):
                    temp_pdf_files.append(temp_pdf)
            elif ext in ['.docx', '.pptx', '.xlsx']:
                # LibreOffice orqali konvertatsiya
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

        # Agar faqat bitta fayl bo‘lsa — uni output_path ga ko‘chir
        if len(temp_pdf_files) == 1:
            os.rename(temp_pdf_files[0], output_path)
        elif len(temp_pdf_files) > 1:
            # Barcha PDF-fayllarni birlashtirish
            from PyPDF2 import PdfMerger
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

def convert_image_to_pdf(image_path, pdf_path):
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        width, height = A4
        img_width, img_height = img.size
        ratio = min(width / img_width, height / img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio
        x = (width - new_width) / 2
        y = (height - new_height) / 2

        c = canvas.Canvas(pdf_path, pagesize=A4)
        c.drawImage(image_path, x, y, width=new_width, height=new_height)
        c.showPage()
        c.save()

        return True
    except Exception as e:
        print(f"[XATO] Rasmni PDF-ga o‘tkazishda xatolik: {e}")
        return False
