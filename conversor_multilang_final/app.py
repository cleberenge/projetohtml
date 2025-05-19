
from flask import Flask, render_template, request, send_file, abort
from werkzeug.utils import secure_filename
import os, io, zipfile
from PIL import Image
from docx import Document
from pdf2docx import Converter
import fitz
from docx2pdf import convert as docx2pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    files = request.files.getlist('files')
    conversion_type = request.form.get('conversion_type')
    if not files or not conversion_type:
        abort(400)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for file in files:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
            if not allowed_file(filename): continue
            try:
                if conversion_type == 'png2jpg' and ext == 'png':
                    img = Image.open(file).convert('RGB')
                    out_name = filename.rsplit('.', 1)[0] + '.jpg'
                    buffer = io.BytesIO()
                    img.save(buffer, 'JPEG')
                    buffer.seek(0)
                    zf.writestr(out_name, buffer.read())
                elif conversion_type == 'jpg2pdf' and ext in ['jpg', 'jpeg']:
                    img = Image.open(file).convert('RGB')
                    out_name = filename.rsplit('.', 1)[0] + '.pdf'
                    buffer = io.BytesIO()
                    img.save(buffer, 'PDF')
                    buffer.seek(0)
                    zf.writestr(out_name, buffer.read())
                elif conversion_type == 'pdf2jpg' and ext == 'pdf':
                    pdf = fitz.open(stream=file.read(), filetype='pdf')
                    for page_num in range(len(pdf)):
                        pix = pdf[page_num].get_pixmap()
                        out_name = f"{filename.rsplit('.', 1)[0]}_page{page_num+1}.jpg"
                        zf.writestr(out_name, pix.tobytes('jpeg'))
                elif conversion_type == 'doc2pdf' and ext == 'docx':
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(temp_path)
                    pdf_path = temp_path.replace('.docx', '.pdf')
                    docx2pdf(temp_path, pdf_path)
                    with open(pdf_path, 'rb') as f: zf.writestr(os.path.basename(pdf_path), f.read())
                    os.remove(temp_path)
                    os.remove(pdf_path)
                elif conversion_type == 'pdf2doc' and ext == 'pdf':
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    doc_path = temp_path.replace('.pdf', '.docx')
                    file.save(temp_path)
                    cv = Converter(temp_path)
                    cv.convert(doc_path, start=0, end=None)
                    cv.close()
                    with open(doc_path, 'rb') as f: zf.writestr(os.path.basename(doc_path), f.read())
                    os.remove(temp_path)
                    os.remove(doc_path)
            except Exception as e:
                print(f"Erro: {e}")
                continue

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip',
                     as_attachment=True, download_name='converted_files.zip')
