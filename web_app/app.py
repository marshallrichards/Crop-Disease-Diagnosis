# written by Marshall Richards 2016
import os
import sys
import shutil
import tensorflow as tf
# in the future I would like to be able to just import label_image and not run the whole thing inside here
# need to figure out how to scope variable globably and have label_image run after image has been copied and saved
# more analysis is needed
# Things to add: a selection and confirmation of what plant you want analyzed
# A more robust data set for many different plants and diseases
# That way once you check what plant you want run the program can select to test against only those images
# and category of that plant and its diseases
# maybe later have a question tree with like; 'does it have spots or just browned leaves?' etc
# to narrow down results
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
UPLOAD_FOLDER = 'uploads/' # directory for data collection to maintain permanent record
TENSOR_FOLDER = 'tensor/'  # so this will be directory to feed file to tensorflow
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

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
            # I think initially it will save here and then be separated later after results
            # to the catergory it was placed in ie healthy or unhealthy file folders
            # instead of one large Upload Folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            shutil.copy((os.path.join(app.config['UPLOAD_FOLDER'], filename)),(os.path.join(app.config['TENSOR_FOLDER'], 'test.jpg')))
            # Decided to compromise and just put the label_image.py code in here
            image_path = 'tensor/test.jpg' 

            # Read in the image_data
            image_data = tf.gfile.FastGFile(image_path, 'rb').read()

            # Loads label file, strips off carriage return
            label_lines = [line.rstrip() for line 
                   in tf.gfile.GFile("retrained_labels.txt")]
            # Unpersists graph from file
            with tf.gfile.FastGFile("retrained_graph.pb", 'rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
                _ = tf.import_graph_def(graph_def, name='')
            with tf.Session() as sess:
                # Feed the image_data as input to the graph and get first prediction
                softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
    
                predictions = sess.run(softmax_tensor, \
                    {'DecodeJpeg/contents:0': image_data})
    
                # Sort to sow labels of first prediction in order of confidence
                top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
            node_id = top_k[0] 
            human_string= label_lines[node_id]
            score = predictions[0][node_id]
            print score
            possibly_delete = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if score >= .80:
                if human_string == 'healthy':
                    return 'Plant is show to be healthy.'
                else:
                    return 'Plant is unhealthy and needs attention.(Eventually this will redirect you to a treatment page.)'
            else:
                #Deletes file because not applicable if tensorflow couldn't match it past 80%
                os.remove(possibly_delete)
                return '''Could not make accurate prediction. File Removed
                        
                        '''
    return '''
    <!doctype html>
    <title>Soy Disease Diagnosis</title>
    <h1>Welcome to Medicine Man v0.1</h1>
    <style>
    h1 {
        text-align:center;
    } 
    form {
        text-align:center;
    }
    </style>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)