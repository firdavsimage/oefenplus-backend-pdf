@app.route("/convert", methods=["POST"])
def convert_to_pdf():
    try:
        if 'files' in request.files:
            files = request.files.getlist("files")
            valid_images = []
            hash_input = b""

            for file in files:
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext in ['jpg', 'jpeg', 'png']:
                    uid = uuid.uuid4().hex
                    filepath = os.path.join(UPLOAD_FOLDER, f"{uid}_{filename}")
                    file.save(filepath)
                    valid_images.append(filepath)
                    hash_input += open(filepath, "rb").read()

            if not valid_images:
                return jsonify({"error": "Rasmlar topilmadi yoki noto‘g‘ri format"}), 400

            hashname = hashlib.md5(hash_input).hexdigest()
            cached_pdf = os.path.join(CACHE_FOLDER, f"{hashname}.pdf")
            if os.path.exists(cached_pdf):
                return send_file(cached_pdf, as_attachment=True)

            # ILovePDF task yaratish
            res = requests.post("https://api.ilovepdf.com/v1/start/imagepdf", json={
                "public_key": ILOVEPDF_SECRET
            })
            if res.status_code != 200:
                return jsonify({"error": "iLovePDF task yaratib bo‘lmadi"}), 500

            task = res.json()
            server, task_id = task["server"], task["task"]

            # Fayllarni yuklash
            for path in valid_images:
                with open(path, "rb") as f:
                    upload_res = requests.post(f"https://{server}/v1/upload", files={
                        'file': (os.path.basename(path), f)
                    }, data={'task': task_id})
                    if upload_res.status_code != 200:
                        return jsonify({"error": "Yuklashda xatolik"}), 500

            # Konvertatsiya qilish
            proc_res = requests.post(f"https://{server}/v1/process", data={"task": task_id})
            if proc_res.status_code != 200:
                return jsonify({"error": "Konvertatsiya xatoligi"}), 500

            # Yuklab olish
            output = requests.get(f"https://{server}/v1/download/{task_id}", stream=True)
            if output.status_code != 200:
                return jsonify({"error": "Yuklab olish xatoligi"}), 500

            with open(cached_pdf, 'wb') as f:
                for chunk in output.iter_content(1024):
                    if chunk:
                        f.write(chunk)

            return send_file(cached_pdf, as_attachment=True)

        # Bitta fayl
        if 'file' not in request.files:
            return jsonify({"error": "Fayl yuborilmadi"}), 400

        file = request.files['file']
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[-1].lower()

        if ext not in ['jpg', 'jpeg', 'png', 'docx', 'pptx']:
            return jsonify({"error": "Yaroqsiz fayl turi"}), 400

        uid = uuid.uuid4().hex
        filepath = os.path.join(UPLOAD_FOLDER, f"{uid}_{filename}")
        file.save(filepath)

        hashname = file_hash(filepath)
        cached_pdf = os.path.join(CACHE_FOLDER, f"{hashname}.pdf")
        if os.path.exists(cached_pdf):
            return send_file(cached_pdf, as_attachment=True)

        # ILovePDF task yaratish
        res = requests.post("https://api.ilovepdf.com/v1/start/convert", json={
            "public_key": ILOVEPDF_SECRET,
            "task": "officepdf" if ext in ["docx", "pptx"] else "imagepdf"
        })
        if res.status_code != 200:
            return jsonify({"error": "iLovePDF task yaratilmadi"}), 500

        task = res.json()
        server, task_id = task["server"], task["task"]

        with open(filepath, "rb") as f:
            upload_res = requests.post(f"https://{server}/v1/upload", files={
                'file': (filename, f)
            }, data={'task': task_id})
            if upload_res.status_code != 200:
                return jsonify({"error": "Yuklashda xatolik"}), 500

        proc_res = requests.post(f"https://{server}/v1/process", data={"task": task_id})
        if proc_res.status_code != 200:
            return jsonify({"error": "Konvertatsiya xatoligi"}), 500

        output = requests.get(f"https://{server}/v1/download/{task_id}", stream=True)
        if output.status_code != 200:
            return jsonify({"error": "Yuklab olish xatoligi"}), 500

        with open(cached_pdf, 'wb') as f:
            for chunk in output.iter_content(1024):
                if chunk:
                    f.write(chunk)

        return send_file(cached_pdf, as_attachment=True)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
