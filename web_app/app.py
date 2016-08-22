import os
import sys
import shutil
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
UPLOAD_FOLDER = '/path/to/uploads'
TENSOR_FOLDER = '/path/to/tensor-feeding-image/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TENSOR_FOLDER'] = TENSOR_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # This will make copy of file so that a record can be kept of every file and tensor can run on a separate test.jpg
            shutil.copy((os.path.join(app.config['UPLOAD_FOLDER'], filename)),(os.path.join(app.config['TENSOR_FOLDER'], 'test.jpg')))
            return 'File Made'
    return '''
    <!doctype html>
    <title>Upload new File now</title>
    <h1>Upload new File now</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)
