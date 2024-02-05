from flask import Flask, render_template, request, session, url_for
import os
import csv
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename
import tensorflow as tf

UPLOAD_FOLDER = os.path.join('staticFiles', 'predict')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, template_folder='templateFiles', static_folder='staticFiles')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'This is your secret key to utilize session in Flask'

model = load_model('C:/Users/Admin/Desktop/pothole&loaded/pothole v2/model.h5')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_pothole(X):
    X_resized = cv2.resize(X, (256, 256))
    X_resized = np.array(X_resized)
    X_resized = np.expand_dims(X_resized, axis=0)

    y_pred = np.round(model.predict(X_resized))
    if np.array_equal(y_pred[0], [1, 0, 0, 0]):
        return "Pothole Road"
    elif np.array_equal(y_pred[0], [0, 1, 0, 0]):
        return "Cracks Road"
    elif np.array_equal(y_pred[0], [0, 0, 1, 0]):
        return "Patches Road"
    else:
        return "Plain Road"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=["POST"])
def uploadFiles():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('uploaded-file')
        file_paths = []

        for uploaded_file in uploaded_files:
            if uploaded_file and allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(file_path)
                file_paths.append(file_path)

        session['uploaded_img_file_paths'] = file_paths

        return render_template('index2.html')

@app.route('/show_image')
def displayImage():
    img_file_paths = session.get('uploaded_img_file_paths', [])
    predictions = {}
    if X is None or X.size == 0:
        predictions[img_file_paths] = "Unable to read or empty image"
    else:
        predictions[img_file_paths] = predict_pothole(X)
    #for img_file_path in img_file_paths:
        #X = cv2.imread(img_file_path, cv2.IMREAD_COLOR)


    # Save predictions to a CSV file
    csv_filename = 'predictions.csv'
    with open(csv_filename, mode='w', newline='') as csv_file:
        fieldnames = ['Image_Path', 'Prediction']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for img_path, prediction in predictions.items():
            writer.writerow({'Image_Path': img_path, 'Prediction': prediction})

    return render_template('show_image.html', predictions=predictions)


if __name__ == '__main__':
    app.run(debug=True)
