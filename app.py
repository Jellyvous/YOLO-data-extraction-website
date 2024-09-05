from flask import Flask, render_template, request, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
from utils.process_image import process_image
from config import UPLOAD_FOLDER, RESULT_FOLDER

app = Flask(__name__)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route('/')
def hello_world():
    return render_template('index.html', name='World')


@app.route('/', methods=['POST', 'GET'])
def predict_img():
    if request.method == 'POST':
        if 'file' in request.files:
            f = request.files['file']
            filename = secure_filename(f.filename)
            filepath = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(filepath)

            result_json_path, processed_image_path = process_image(filepath, filename)

            return send_file(result_json_path, as_attachment=True)


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
