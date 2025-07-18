from flask import Flask, request, send_file, render_template
import requests
import os
import uuid
import shutil

app = Flask(__name__)
PUBLIC_KEY = "YOUR_PUBLIC_KEY_HERE"  # ILovePDF API public key

# Ruxsat berilgan fayl turlari
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
DOC_EXTENSIONS = {'.doc', '.docx', '.ppt', '.pptx'}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/convert', methods=['POST'])
def convert_files():
    uploaded_files = request.files.getlist("files")
    temp_dir = os.path.join("temp", str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # 1. Auth
        auth = requests.post("https://api.ilovepdf.com/v1/auth", json={"public_key": PUBLIC_KEY})
        auth.raise_for_status()
        token = auth.json()['token']

        # Fayllarni turlarga ajratamiz
        image_files, doc_files = [], []
        for file in uploaded_files:
            ext = os.path.splitext(file.filename)[1].lower()
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)
            if ext in IMAGE_EXTENSIONS:
                image_files.append(file_path)
            elif ext in DOC_EXTENSIONS:
                doc_files.append(file_path)

        merged_pdfs = []

        # 🔄 2. Rasmlarni PDF ga aylantirish
        if image_files:
            img_pdf = convert_with_ilovepdf(token, image_files, 'jpgtopdf', temp_dir, 'images.pdf')
            if img_pdf:
                merged_pdfs.append(img_pdf)

        # 🔄 3. DOC/PPT fayllarni PDF ga aylantirish
        if doc_files:
            doc_pdf = convert_with_ilovepdf(token, doc_files, 'officepdf', temp_dir, 'docs.pdf')
            if doc_pdf:
                merged_pdfs.append(doc_pdf)

        # 🔄 4. Barcha PDF’larni birlashtirish
        if len(merged_pdfs) > 1:
            final_pdf = merge_pdfs(token, merged_pdfs, temp_dir)
        elif len(merged_pdfs) == 1:
            final_pdf = merged_pdfs[0]
        else:
            return "Hech qanday mos fayl topilmadi.", 400

        return send_file(final_pdf, as_attachment=True)

    except Exception as e:
        return f"Xatolik: {str(e)}", 500
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def convert_with_ilovepdf(token, file_paths, task_type, temp_dir, output_name):
    # 1. Task yaratish
    start = requests.post(f"https://api.ilovepdf.com/v1/start/{task_type}", headers={
        "Authorization": f"Bearer {token}"
    })
    start.raise_for_status()
    task = start.json()['task']
    server = start.json()['server']

    # 2. Yuklash
    server_filenames = []
    for file_path in file_paths:
        with open(file_path, 'rb') as f:
            upload = requests.post(f"https://{server}/v1/upload", headers={
                "Authorization": f"Bearer {token}"
            }, files={"file": f}, data={"task": task})
            upload.raise_for_status()
            server_filenames.append(upload.json()['server_filename'])

    # 3. Process
    files_payload = [{"server_filename": name} for name in server_filenames]
    process = requests.post(f"https://{server}/v1/process", headers={
        "Authorization": f"Bearer {token}"
    }, json={
        "task": task,
        "files": files_payload,
        "output_filename": output_name
    })
    process.raise_for_status()

    # 4. Yuklab olish
    download = requests.get(f"https://{server}/v1/download/{task}", headers={
        "Authorization": f"Bearer {token}"
    })
    output_file = os.path.join(temp_dir, output_name)
    with open(output_file, 'wb') as f:
        f.write(download.content)

    return output_file


def merge_pdfs(token, pdf_paths, temp_dir):
    # Start task
    start = requests.post("https://api.ilovepdf.com/v1/start/merge", headers={
        "Authorization": f"Bearer {token}"
    })
    start.raise_for_status()
    task = start.json()['task']
    server = start.json()['server']

    # Upload PDFs
    server_filenames = []
    for pdf in pdf_paths:
        with open(pdf, 'rb') as f:
            upload = requests.post(f"https://{server}/v1/upload", headers={
                "Authorization": f"Bearer {token}"
            }, files={"file": f}, data={"task": task})
            upload.raise_for_status()
            server_filenames.append(upload.json()['server_filename'])

    # Process
    files_payload = [{"server_filename": name} for name in server_filenames]
    process = requests.post(f"https://{server}/v1/process", headers={
        "Authorization": f"Bearer {token}"
    }, json={
        "task": task,
        "files": files_payload,
        "output_filename": "converted_final.pdf"
    })
    process.raise_for_status()

    # Download
    download = requests.get(f"https://{server}/v1/download/{task}", headers={
        "Authorization": f"Bearer {token}"
    })
    output_file = os.path.join(temp_dir, "converted_final.pdf")
    with open(output_file, 'wb') as f:
        f.write(download.content)

    return output_file


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
