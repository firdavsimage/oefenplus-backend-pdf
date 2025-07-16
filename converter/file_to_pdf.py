import os
from docx2pdf import convert as convert_docx2pdf
import pandas as pd
from reportlab.pdfgen import canvas

# DOCX faylni PDFga o‘girish
def convert_docx(input_path, output_folder):
    output_path = os.path.join(output_folder, os.path.basename(input_path).replace('.docx', '.pdf'))
    convert_docx2pdf(input_path, output_path)
    return output_path

# PPTX faylni PDFga o‘girish - faqat Windows uchun
def convert_pptx(input_path, output_folder):
    try:
        import comtypes.client
    except ImportError:
        raise RuntimeError("PPTX konvertatsiyasi faqat Windows tizimida ishlaydi (comtypes kerak).")

    output_path = os.path.join(output_folder, os.path.basename(input_path).replace('.pptx', '.pdf'))

    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1
    presentation = powerpoint.Presentations.Open(input_path)
    presentation.SaveAs(output_path, 32)  # 32 = PDF format
    presentation.Close()
    powerpoint.Quit()

    return output_path

# XLSX faylni PDFga o‘girish
def convert_xlsx(input_path, output_folder):
    df = pd.read_excel(input_path)
    output_path = os.path.join(output_folder, os.path.basename(input_path).replace('.xlsx', '.pdf'))

    c = canvas.Canvas(output_path)
    text = c.beginText(40, 800)

    for col in df.columns:
        text.textLine(f"{col}: {', '.join([str(i) for i in df[col].values])}")
        text.textLine("")

    c.drawText(text)
    c.save()

    return output_path

# Umumiy dispatcher
def convert_file(file_path, output_folder):
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".docx":
        return convert_docx(file_path, output_folder)
    elif ext == ".pptx":
        return convert_pptx(file_path, output_folder)
    elif ext == ".xlsx":
        return convert_xlsx(file_path, output_folder)
    else:
        raise ValueError("Qo‘llab-quvvatlanmaydigan fayl turi.")
