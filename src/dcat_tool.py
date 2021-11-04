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

import openpyxl
import rdflib
from rdflib import Dataset, Graph, URIRef, Literal, Namespace

import template_reader
import dhs_ontology
import easy_workbook

INSTRUCTIONS  = os.path.join(dirname(abspath( __file__ )) , "instructions.md")

def make_template(fname, include_instructions, schemata_dir=dhs_ontology.SCHEMATA_DIR, schema=dhs_ontology.COLLECT_TTL, debug=False):
    g = dhs_ontology.dcatv3_ontology(schemata_dir, schema)
    (g2, ci_objs) = dhs_ontology.get_template_column_info_objs(g, dhs_ontology.CI_QUERY, debug=debug)
    eg = easy_workbook.ExcelGenerator()
    if include_instructions:
        eg.add_markdown_sheet("Instructions", open(INSTRUCTIONS).read())
    eg.add_columns_sheet("Inventory", ci_objs)
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
    parser.add_argument("--validate", help="Read a JSON object on stdin and validate it, with output being another JSON object on stdout.",
                        action='store_true')
    args = parser.parse_args()

    if args.dump:
        print("Dumping triple store:\n")
        for stmt in sorted( dhs_ontology.dcatv3_ontology(args.schemata_dir, args.schema) ):
            pprint.pprint(stmt)
            print()

    if args.validate:
        v = dhs_ontology.Validator( args.schemata_dir, args.schema )
        while not sys.stdin.eof():
            jin  = json.load( sys.stdin )
            jout = validate( jin )
        json.dump(sys.stdout, jout, indent=4)
        sys.stdout.write("\n")

    if args.make_template:
        make_template(args.make_template, not args.noinstructions, schemata_dir=args.schemata_dir, schema=args.schema, debug=args.debug)

    if args.read_xlsx:
        for r in read_xlsx(args.read_xlsx):
            print(r)

    if args.writeschema:
        fmt = os.path.splitext(args.write)[1][1:].lower()
        if fmt=='json':
            fmt='json-ld'
        g2.serialize(destination=args.write, format=fmt)
