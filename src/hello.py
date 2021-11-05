import os
import uuid
import tempfile
import sys
import json
import logging
import time

from os.path import dirname,basename,abspath

# This is required because Flask changes the current directory.
MYDIR = dirname( abspath( __file__ ))
if MYDIR not in sys.path:
    sys.path.append(MYDIR)

import dcat_tool
import dhs_ontology

# Bring in flask

from flask import Flask, session, flash, request, redirect, send_from_directory, render_template, send_file
from werkzeug.utils import secure_filename
from flask.helpers import safe_join

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
static_dir = safe_join(os.path.dirname(__file__), 'static')

# Do not cache anything
@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response

# Route the home page
@app.route('/', methods=['GET'])
def _home():
    return render_template('index.html')


# Validation
print(">> Loading validator...")
t0 = time.time()
validator = dhs_ontology.Validator()
t = time.time() - t0
print(">> Validator loaded in",t,"seconds")
def web_analyze(obj, msg):
    """
    Analyze an object that is uploaded and report the results via flash(), with each result preceeded by msg.
    """
    try:
        validator.add_row( obj )
        flash( msg+"validates")
    except dhs_ontology.ValidationFail as e:
        flash( msg+"does not validate -- "+str(e))

@app.route('/validate/xlsx', methods=['POST'])
def _validate_xlsx():
    """
    This is the main REST API for validating .xlsx files.
    It has result code feedback
    """
    with tempfile.NamedTemporaryFile( suffix='.xlsx' ) as tf:
        file.save( tf.name )
        resp = validate_xlsx( tf.name )
        code = 200
        if (resp['error']):
            code=409
        return resp, code


@app.route('/', methods=['POST'])
def _upload_file_or_json():
    """
    This is the main user interface for posting files and text fields
    it includes HTML feedback.
    """
    if 'file' in request.files:
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
        if ext=='.xls':
            flash(".xls files must be converted to .xlsx prior to uploading.")
            return redirect(request.url)
        with tempfile.NamedTemporaryFile( suffix=ext ) as tf:
            file.save( tf.name )
            return redirect(request.url)
    try:
        text = request.form['text'].strip()
    except (KeyError, ValueError) as e:
        flash('no text provided')
        return redirect(request.url)
    if text:
        try:
            obj = json.loads(text)
            flash('JSON is syntactically valid.')
        except json.decoder.JSONDecodeError as e:
            flash('JSON is not valid.')
            return redirect(request.url)

        if isinstance(obj,list):
            plural = '' if len(obj)==1 else 's'
            flash(f'A JSON list with {len(obj)} element{plural} was provided')
            validator.clear()
            for (ct,o) in enumerate(obj,1):
                web_analyze(o,f"object #{ct}:")
        elif isinstance(obj,dict):
            flash('A JSON object was provided')
            web_analyze(o,"")
        else:
            flash('Error: a JSON list or object must be provided.')
        return redirect(request.url)

    flash('Please provide text or a file to analyze.')
    return redirect(request.url)


#
# Generate a template
#
@app.route('/DIP_Template.xlsx')
def _template():
    with tempfile.NamedTemporaryFile( suffix='.xlsx' ) as tf:
        dcat_tool.make_template( tf.name, True )
        return send_file(tf.name,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         attachment_filename='DIP_Template.xlsx', as_attachment=True)

#
# Serve static files
#
@app.route('/<path:path>', methods=['GET'])
def _static(path):
    return send_from_directory(static_dir, path)
