from flask import Flask, render_template, request, redirect, url_for, jsonify
import numpy as np
import cv2
import os
import base64
from voice_commands import recognize_command

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'C:/Users/hp/OneDrive/Documents/DURHAM/AIDI SEM 2/AIDI 2005/project/upload/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_to_sketch(image_path, colored=False):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted_image = cv2.bitwise_not(gray_image)
    blur_image = cv2.GaussianBlur(inverted_image, (21, 21), sigmaX=0, sigmaY=0)
    inverted_blur = cv2.bitwise_not(blur_image)
    sketch_image = cv2.divide(gray_image, inverted_blur, scale=256.0)
    if colored:
        sketch_image = cv2.cvtColor(sketch_image, cv2.COLOR_GRAY2BGR)
    return sketch_image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('edit_file', filename=filename))
    return render_template('upload.html')

@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if request.method == 'POST':
        colored = 'colored' in request.form
        sketch_image = convert_to_sketch(file_path, colored)
        _, buffer = cv2.imencode('.png', sketch_image)
        sketch_data = base64.b64encode(buffer).decode('utf-8')
        return render_template('edit.html', sketch_data=sketch_data)
    return render_template('edit.html', filename=filename)

@app.route('/voice-command', methods=['POST'])
def voice_command():
    command = request.json.get('command')
    result = recognize_command(command)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
