import os
import uuid
import tempfile

from flask import Flask, session, flash, request, redirect, send_from_directory, render_template
from werkzeug.utils import secure_filename
from flask.helpers import safe_join


app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
#app.config['SESSION_TYPE'] = 'filesystem'
#sess = session.Session()

static = safe_join(os.path.dirname(__file__), 'static')


@app.route("/hello")
def hello():
    return "Hello, World!"

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    filename = secure_filename(file.filename)
    (base,ext)  = os.path.splitext(filename)
    ext = ext.lower()
    if filename == '':
        flash('No selected file')
        return redirect(request.url)
    if ext=='.pdf':
        flash('PDF files are not accepted.')
        return redirect(request.url)
    if ext=='.pdf':
        flash('PDF files are not accepted.')
        return redirect(request.url)
    if ext=='.xls':
        flash(".xls files must be converted to .xlsx prior to uploading.")
        return redirect(request.url)
    with tempfile.NamedTemporaryFile( suffix=ext ) as tf:
        file.save( tf.name )
        flash('saved as '+tf.name)
        return redirect(request.url)

@app.route('/', methods=['GET'])
def _home():
    #return send_from_directory(static, 'index.html')
    return render_template('index.html')

@app.route('/<path:path>', methods=['GET'])
def _static(path):
    return send_from_directory(static, path)
