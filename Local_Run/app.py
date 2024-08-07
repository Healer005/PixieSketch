from flask import Flask, render_template, request, redirect, url_for, jsonify
import numpy as np
import cv2
import os
import base64
from voice_commands import recognize_command

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r'C:\Users\vybha\Desktop\TK\Capstone\PixieSketch\Local_Run\upload'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_to_sketch(image_path, colored=False):
    # Step 1: Read the image
    image = cv2.imread(image_path)
    
    # Step 2: Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Step 3: Invert the grayscale image
    inverted_image = cv2.bitwise_not(gray_image)
    
    # Step 4: Apply Gaussian Blur to the inverted image
    blur_image = cv2.GaussianBlur(inverted_image, (21, 21), sigmaX=0, sigmaY=0)
    
    # Step 5: Invert the blurred image
    inverted_blur = cv2.bitwise_not(blur_image)
    
    # Step 6: Create the pencil sketch effect by dividing the grayscale image by the inverted blurred image
    sketch_image = cv2.divide(gray_image, inverted_blur, scale=256.0)
    
    if colored:
        # If colored is True, combine the sketch with the original image's color
        # Step 7: Create a color sketch by blending the original image with the sketch
        color_image = cv2.cvtColor(sketch_image, cv2.COLOR_GRAY2BGR)
        blended = cv2.addWeighted(image, 0.6, color_image, 0.4, 0)
        return blended
    
    # Convert the sketch image to BGR before returning
    return cv2.cvtColor(sketch_image, cv2.COLOR_GRAY2BGR)

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
