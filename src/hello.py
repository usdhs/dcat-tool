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

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_JSON_DECODE_ERROR = 409

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


################################################################
### Load the validator. This is slow, so we do it when the package loads
print(">> Loading validator...")
t0 = time.time()
validator = dhs_ontology.Validator()
t = time.time() - t0
print(">> Validator loaded in",t,"seconds")
################################################################


@app.route('/validate/xlsx', methods=['POST'])
def _validate_xlsx():
    """
    This is the main REST API for validating .xlsx files.
    It has result code feedback.
    @param request.files['file'] - the input file, from a posted form.
    @return -  json encoded string of ret, and the code
    """
    file = request.files['file']

    with tempfile.NamedTemporaryFile( suffix='.xlsx', delete=False ) as tf:
        file.save( tf.name )
        ret = dhs_ontology.validate_xlsx( validator, tf.name )
    if ( ret.get('error','') ):
        ret['response'] = HTTP_JSON_DECODE_ERROR
    if 'response' not in ret:
        ret['response'] = HTTP_OK
    return json.dumps(ret, default=str), ret['response']


@app.route('/validate/json', methods=['POST'])
def _validate_json():
    """
    This is the main REST API for validating JSON.
    It has result code feedback. It mirrors the code below.
    @param request.form['text'] - the text to validate.
    """
    try:
        obj = json.loads( request.form['text'] )
    except json.decoder.JSONDecodeError as e:
        return "JSON decode error",HTTP_JSON_DECODE_ERROR
    ret = {}
    ret['messages'] = []
    ret['response']     = HTTP_OK
    if isinstance(obj,dict):
        obj = [obj]             # wrap it
    if isinstance(obj,list):
        validator.clear()
        for o in obj:
            try:
                validator.add_row( o )
                ret['messages'].append('OK')
            except dhs_ontology.ValidationFail as e:
                ret['messages'].append('FAIL: '+str(e))
                ret['response'] = HTTP_BAD_REQUEST
    else:
        ret['messages'].append('A JSON list or object must be provided')
        ret['response'] = HTTP_BAD_REQUEST
    return json.dumps(ret, default=str), ret['response']


################################################################
## Handle post to / , which is done by the web page.
## Arguments:
## request.files['file'] - the file that is uploaded
## request.form['text']  - the text to validate
@app.route('/', methods=['POST'])
def _upload_file_or_json():
    """
    This is the main user interface for posting files and text fields
    it includes HTML feedback. It calls the same functions as used by the REST API.
    """
    # Test the Excel validator. This uses the same code as the actual validator above
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

        # Use the API
        (resp_json, code) = _validate_xlsx()
        resp = json.loads( resp_json )
        for msg in resp['messages']:
            flash(msg)
        flash("Return code: "+str(resp['response']))
        return redirect(request.url)


    # Test the JSON validator
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
            flash('JSON is not syntatically valid.')
            return redirect(request.url)

        (resp_json,code) = _validate_json()
        try:
            resp = json.loads( resp_json )
        except json.decoder.JSONDecodeError as e:
            print("invalid resp_json: ", resp_json)
            flash('Internal Error')
            return redirect(request.url)

        for msg in resp['messages']:
            flash(msg)
        flash("Return code: "+str(resp['response']))
        return redirect(request.url)

    flash('Please provide text or a file to analyze.')
    return redirect(request.url)


#
# Generate a template
#
@app.route('/DIP_Template.xlsx')
def _template():
    with tempfile.NamedTemporaryFile( suffix='.xlsx', delete=False ) as tf:
        dcat_tool.make_template( validator, tf.name, True )
        return send_file(tf.name,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         attachment_filename='DIP_Template.xlsx', as_attachment=True)

#
# Serve static files
#
@app.route('/<path:path>', methods=['GET'])
def _static(path):
    return send_from_directory(static_dir, path)
