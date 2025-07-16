from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def convert_docx_to_pdf(input_path, output_path):
    doc = Document(input_path)
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    textobject = c.beginText(50, height - 50)
    textobject.setFont("Helvetica", 12)

    for para in doc.paragraphs:
        for line in para.text.splitlines():
            textobject.textLine(line)
    c.drawText(textobject)
    c.showPage()
    c.save()
