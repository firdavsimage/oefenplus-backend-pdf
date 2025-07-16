from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import os

def convert_files(input_paths, output_path):
    try:
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        for path in input_paths:
            try:
                img = Image.open(path)
                img = img.convert("RGB")
                img_width, img_height = img.size
                ratio = min(width / img_width, height / img_height)
                new_width = img_width * ratio
                new_height = img_height * ratio
                x = (width - new_width) / 2
                y = (height - new_height) / 2

                temp_img_path = "temp.jpg"
                img.save(temp_img_path, dpi=(300, 300))

                c.drawImage(temp_img_path, x, y, width=new_width, height=new_height)
                c.showPage()
                os.remove(temp_img_path)

            except Exception as e:
                print(f"[XATO] {path} rasmni chizishda xato: {e}")
                continue

        c.save()
        return True
    except Exception as e:
        print(f"[XATO] PDF yaratishda xatolik: {e}")
        return False
