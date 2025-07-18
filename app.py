from flask import Flask, request, send_file, render_template
import convertapi
import os
import uuid
import shutil

app = Flask(__name__)

# ConvertAPI secret key (ConvertAPI bilan ishlaydi)
convertapi.api_secret = 'your_actual_convertapi_secret_key'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/convert', methods=['POST'])
def convert_files():
    uploaded_files = request.files.getlist("files")
    temp_dir = os.path.join("temp", str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)

    # Save uploaded files
    input_paths = []
    for file in uploaded_files:
        filepath = os.path.join(temp_dir, file.filename)
        file.save(filepath)
        input_paths.append(filepath)

    try:
        # Convert to PDF
        result = convertapi.convert('pdf', {
            'Files': input_paths
        })

        output_file = os.path.join(temp_dir, 'converted.pdf')
        result.file.save(output_file)

        return send_file(output_file, as_attachment=True)

    finally:
        # Clean up all temp files after response is sent
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
