from flask import Flask, request, render_template, jsonify
import requests
import os

app = Flask(__name__)
SECRET = 'secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d'

def get_convert_endpoint(filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext in ['jpg', 'jpeg', 'png']:
        return 'jpg/to/pdf'
    if ext in ['doc', 'docx']:
        return 'docx/to/pdf'
    if ext in ['ppt', 'pptx']:
        return 'pptx/to/pdf'
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_files():
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'Hech qanday fayl tanlanmagan'}), 400

    pdf_urls = []

    for file in files:
        endpoint = get_convert_endpoint(file.filename)
        if not endpoint:
            return jsonify({'error': f"Qo‘llab-quvvatlanmaydigan format: {file.filename}"}), 400

        res = requests.post(
            f'https://v2.convertapi.com/convert/{endpoint}?Secret={SECRET}',
            files={'file': (file.filename, file.stream)}
        )
        data = res.json()
        if 'Files' in data and data['Files']:
            pdf_urls.append(data['Files'][0]['Url'])
        else:
            return jsonify({'error': f'Xatolik: {file.filename}'}), 500

    # Birlashtirish
    merge_data = {'Files': pdf_urls}
    res = requests.post(
        f'https://v2.convertapi.com/convert/merge/pdf?Secret={SECRET}',
        json=merge_data
    )
    merge_result = res.json()

    if 'Files' in merge_result and merge_result['Files']:
        final_url = merge_result['Files'][0]['Url']
        return jsonify({'pdf': final_url})
    else:
        return j
