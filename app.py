from flask import Flask, request, send_file, render_template
import convertapi
import os
import uuid

convertapi.api_secret = 'secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/convert', methods=['POST'])
def convert_files():
    uploaded_files = request.files.getlist("files")
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    file_paths = []
    for file in uploaded_files:
        path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
        file.save(path)
        file_paths.append(path)

    result = convertapi.convert('pdf', {'Files': file_paths})
    output_file = os.path.join(temp_dir, f"{uuid.uuid4()}_merged.pdf")
    result.file.save(output_file)

    return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
