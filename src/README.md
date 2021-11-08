# Contents

This directory contains the python source code for:


1. Creating the Excel collection instrument that may be used by some
   organizations to assist in collecting data inventory records. The
   fields in the Excel instrument are specified in the document
   [dhs_collect.ttl](../schemata/dhs_collect.ttl)

2. Parsing filled-out collection instruments into JSON. (Each row
   becomes a JSON object.)

3. Validating single JSON data inventory objects and collections of JSON objects, the
   key difference being that a collections are validated to make sure
   that they do not contain duplicate unique identifiers. Currently
   validation is done with hard-coded python; it should be moved to
   [SHACL (Shape Constraint Langauge)](https://www.w3.org/TR/shacl/)

4. A [Python Flask](https://flask.palletsprojects.com/en/2.0.x/) and
   [WSGI-based implementation](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface)
   of an API that validates Excel spreadsheets and JSON objects.

4. A mini-webserver written using the Flask debug webserver.

# Validation Report
The validation report is a JSON object that contains the following
fields:

|field|Purpose|
|----------|-----------|
|result    | HTTP-style result code. 200 if validation is successful, 409 if it is not.|
|records   | List of records that were validated
|messages  | List of (record number, validation error) for records that failed validation.|
|rdf/json  | RDF/JSON of the Excel spreadsheet.|
