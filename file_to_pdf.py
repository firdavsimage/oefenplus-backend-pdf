def convert_image_to_pdf(image_path, pdf_path):
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        img_width, img_height = img.size

        # Avtomatik orientatsiya tanlash
        if img_width > img_height:
            # Landscape
            page_size = (A4[1], A4[0])
        else:
            # Portrait
            page_size = A4

        page_width, page_height = page_size
        ratio = min(page_width / img_width, page_height / img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2

        c = canvas.Canvas(pdf_path, pagesize=page_size)
        c.drawImage(image_path, x, y, width=new_width, height=new_height)
        c.showPage()
        c.save()

        return True
    except Exception as e:
        print(f"[XATO] Rasmni PDF-ga o‘tkazishda xatolik: {e}")
        return False
