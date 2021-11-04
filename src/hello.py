import os
import uuid
import tempfile
import sys
from os.path import dirname,basename,abspath

MYDIR = dirname( abspath( __file__ ))
if MYDIR not in sys.path:
    sys.path.append(MYDIR)

import dcat_tool

from flask import Flask, session, flash, request, redirect, send_from_directory, render_template, send_file
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

@app.route('/DIP_Template.xlsx')
def _template():
    with tempfile.NamedTemporaryFile( suffix='.xlsx' ) as tf:
        dcat_tool.make_template( tf.name, True )
        return send_file(tf.name,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         attachment_filename='DIP_Template.xlsx', as_attachment=True)

@app.route('/<path:path>', methods=['GET'])
def _static(path):
    return send_from_directory(static, path)
