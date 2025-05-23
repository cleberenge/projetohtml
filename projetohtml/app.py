from flask import Flask, request, render_template, send_file
from moviepy.editor import VideoFileClip
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    file = request.files['video']
    if not file:
        return "Nenhum vídeo enviado", 400
    input_path = f"input_{file.filename}"
    output_path = f"compressed_{file.filename}"
    file.save(input_path)
    clip = VideoFileClip(input_path)
    clip.write_videofile(output_path, bitrate="500k")
    return send_file(output_path, as_attachment=True)