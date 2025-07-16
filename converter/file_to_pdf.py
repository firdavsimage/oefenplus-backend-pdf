from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def convert_files(image_paths, output_path):
    try:
        a4_width, a4_height = A4
        c = canvas.Canvas(output_path, pagesize=A4)

        for path in image_paths:
            img = Image.open(path)
            img = img.convert('RGB')

            # DPI 300 va A4 o'lchamiga moslashtirish
            img_width, img_height = img.size
            aspect = img_width / img_height
            page_aspect = a4_width / a4_height

            if aspect > page_aspect:
                # Rasm eniga qarab moslashtirish
                new_width = a4_width
                new_height = a4_width / aspect
            else:
                # Rasm bo'yiga qarab moslashtirish
                new_height = a4_height
                new_width = a4_height * aspect

            x = (a4_width - new_width) / 2
            y = (a4_height - new_height) / 2

            temp_img_path = path + "_resized.jpg"
            img.save(temp_img_path, dpi=(300, 300))

            c.drawImage(temp_img_path, x, y, width=new_width, height=new_height)
            os.remove(temp_img_path)
            c.showPage()

        c.save()
        return True
    except Exception as e:
        print(f"[XATO] {e}")
        return False
