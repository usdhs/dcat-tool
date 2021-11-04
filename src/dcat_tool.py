#!/usr/bin/env python3
"""
List datasets and other information

"""

import os
import os.path
from os.path import abspath, dirname
import sys
import pprint
import glob
import time
import json

import openpyxl
import rdflib
from rdflib import Dataset, Graph, URIRef, Literal, Namespace

import template_reader
import dhs_ontology
import easy_workbook

INSTRUCTIONS  = os.path.join(dirname(abspath( __file__ )) , "instructions.md")

def make_template(fname, include_instructions, schemata_dir=dhs_ontology.SCHEMATA_DIR, schema_file=dhs_ontology.COLLECT_TTL, debug=False):
    v = dhs_ontology.Validator(schemata_dir, schema_file)
    eg = easy_workbook.ExcelGenerator()
    if include_instructions:
        eg.add_markdown_sheet("Instructions", open(INSTRUCTIONS).read())
    eg.add_columns_sheet("Inventory", v.ci_objs)
    eg.save( fname )

def read_xlsx(fname) :
    tr = template_reader.TemplateReader( fname )
    return list(tr.inventory_records())


if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Use a DCAT schema to produce capture instruments and APIs.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--schemata_dir",
                        help="specify the directory to read all the schemata. If the --schema file is in schemata_dir, it will only be read once.",
                        default=dhs_ontology.SCHEMATA_DIR)
    parser.add_argument("--schema",
                        help="specify the collection schema file in Turtle, RDF/XML or RDF/JSON",
                        default=dhs_ontology.COLLECT_TTL)
    parser.add_argument("--debug", help="Enable debugging", action='store_true')
    parser.add_argument("--dump", help="Dump the triple store after everything it is read", action='store_true')
    parser.add_argument("--writeschema", help="write the schema to the specified file")
    parser.add_argument("--make_template",
                        help="specify the output filename of the Excel template to make for a collection schema")
    parser.add_argument("--read_xlsx", help="Read a filled-out Excel template and generate an output file")
    parser.add_argument("--noinstructions", help="Do not generate instructions. Mostly for debugging.",
                        action='store_true')
    parser.add_argument("--validate", help="Read a single JSON object on stdin and validate.",
                        action='store_true')
    parser.add_argument("--validate_lines", help="Read multiple JSON objects on stdin and validate all.",
                        action='store_true')
    args = parser.parse_args()

    if args.dump:
        print("Dumping triple store:\n")
        for stmt in sorted( dhs_ontology.dcatv3_ontology(args.schemata_dir, args.schema) ):
            pprint.pprint(stmt)
            print()

    if args.validate:
        v = dhs_ontology.Validator( args.schemata_dir, args.schema )
        data = sys.stdin.readline()
        try:
            jin  = json.loads( data )
        except json.decoder.JSONDecodeError as e:
            print(e)
            print("offending input: ",data)
        try:
            v.validate( jin )
            print("OK")
        except dhs_ontology.ValidationFail as e:
            print("FAIL:"+e.message)

    if args.validate_lines:
        v = dhs_ontology.Validator( args.schemata_dir, args.schema )
        fail = []
        line = 0
        while True:
            data = sys.stdin.readline()
            if len(data) == 0:
                break
            line += 1
            try:
                jin  = json.loads( data )
            except json.decoder.JSONDecodeError as e:
                fail.append([line, e.message])
                continue
            try:
                v.validate( jin )
            except dhs_ontology.ValidationFail as e:
                fail.append([line,e.message])
                continue
        if not fail:
            print("OK")
        else:
            print("FAILURE:")
            for (line, message) in fail:
                print(f"line {line}: {message}")


    if args.make_template:
        make_template(args.make_template, not args.noinstructions, schemata_dir=args.schemata_dir, schema_file=args.schema, debug=args.debug)

    if args.read_xlsx:
        for r in read_xlsx(args.read_xlsx):
            print( json.dumps(r) )

    if args.writeschema:
        fmt = os.path.splitext(args.write)[1][1:].lower()
        if fmt=='json':
            fmt='json-ld'
        g2.serialize(destination=args.write, format=fmt)
