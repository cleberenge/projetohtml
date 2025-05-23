from flask import Flask, render_template, request, send_file
from PIL import Image
import os
import zipfile
from io import BytesIO

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    files = request.files.getlist('images')
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file in files:
            if file and file.filename.endswith(('.png', '.jpeg', '.bmp', '.gif')):
                img = Image.open(file.stream)
                output_filename = os.path.splitext(file.filename)[0] + ".jpg"
                img_path = os.path.join(CONVERTED_FOLDER, output_filename)
                img.convert("RGB").save(img_path, "JPEG")
                zip_file.write(img_path, arcname=output_filename)

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='converted_images.zip')

if __name__ == '__main__':
    app.run(debug=True)