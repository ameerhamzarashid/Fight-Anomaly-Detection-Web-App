import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from flask import jsonify
from werkzeug.utils import secure_filename

import torch
from utils.Fight_utils import loadModel, predict_on_video,start_streaming

torch.backends.cudnn.benchmark = True

print("Loading Model ...")
model = loadModel("model_16_m3_0.8888.pth")
print("Model Loaded ...")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = "12345678"
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_video():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	else:
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print('upload_video filename: ' + filename)
		flash('Video successfully uploaded and displayed below')
		return render_template('upload.html', filename=filename)

@app.route('/display/<filename>')
def display_video(filename):
	#print('display_video filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/analyze_video', methods=['POST'])
def analyze_video():
    data = request.json
    filename = data.get('filename')
    full_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_video_path = filename.split('.')[0] + "_output.mp4"

    predict_on_video(
        full_file_path, 
        output_video_path , 
        model, 16, 2, True) 
      
    result = "Video analysis completed on " + filename

    return jsonify({"Result": result})


if __name__ == '__main__':
    app.run(debug=True)

