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

RDFS          = Namespace("http://www.w3.org/2000/01/rdf-schema#")
XSD           = Namespace("http://www.w3.org/2001/XMLSchema#")
INSTRUCTIONS  = os.path.join(dirname(abspath( __file__ )) , "instructions.md")
DEFAULT_WIDTH = 15              # Excel spreadsheet default width
DEFAULT_TYPE  = XSD.string

def make_template(fname, include_instructions, schema_dir=dhs_ontology.SCHEMATA_DIR, schema=dhs_ontology.COLLECT_TTL):
    g = dhs_ontology.dcatv3_ontology(schema_dir, schema)
    (g2, ci_objs) = get_template_column_info_objs(g, dhs_ontology.CI_QUERY)
    eg = easy_workbook.ExcelGenerator()
    if include_instructions:
        eg.add_markdown_sheet("Instructions", open(INSTRUCTIONS).read())
    eg.add_columns_sheet("Inventory", ci_objs)
    eg.save( fname )

def read_xlsx(fname) :
    tr = template_reader.TemplateReader( fname )
    return list(tr.inventory_records())


class Simplifier:
    def __init__(self, graph):
        self.graph = graph
    def simplify(self, token, namespace=True):
        for prefix,ns in self.graph.namespaces():
            if ns:
                if token.startswith(ns):
                    if namespace:
                        return prefix+":"+token[len(ns):]
                    else:
                        return token[len(ns):]
        return token

def get_template_column_info_objs(g, query):
    # g2 is an output graph of the terms in the collection instrument

    g2 = Graph()

    # Copy over the namespaces from the triples we read to the graph we are producing
    for ns_prefix,namespace in g.namespaces():
        g2.bind(ns_prefix, namespace)

    ci_objs = []
    simp = Simplifier(g)
    for r in g.query( query ):
        d = r.asdict()

        if args.debug:
            print(d)

        if should_skip(d):
            if args.debug:
                print(">> skip")
            continue

        try:
            title = d['aTitle']
        except KeyError:
            title = simp.simplify(d['aProperty'], namespace=False)

        # For the comment, grab the shape comment if it is present. otherwise, grab the property comment.
        # The comment goes into the tooltip for the column
        comment = d.get('aShapeComment', d.get('aPropertyComment', ''))
        if not comment:
            print("Need description for",d['aProperty'])

        obj = easy_workbook.ColumnInfo(value = title, # what is displayed in cell
                                       comment = title + ":\n" + comment,
                                       author = simp.simplify(d['aProperty']),
                                       width = int(d.get('aWidth',DEFAULT_WIDTH)),
                                       typ = simp.simplify(d.get('aType', DEFAULT_TYPE)),
                                       group = d.get('aGroup',''),
                                       )

        # Add the object to the column list
        ci_objs.append( obj )

        # Now create the collection graph
        try:
            g2.add( (d['aProperty'], RDFS.range,   d['aType']) )
        except KeyError as e:
            pass

        try:
            g2.add( (d['aProperty'], RDFS.comment,   d['aComment']) )
        except KeyError as e:
            pass
    return (g2, ci_objs)


def should_skip(d):
    """Skip query responses that are not in English"""
    # Skip property comments that are not in english
    try:
        if d['aPropertyComment'].language != 'en':
            return True
    except (KeyError,AttributeError) as e:
        pass
    return False

if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Use a DCAT schema to produce capture instruments and APIs.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--schema_dir",
                        help="specify the directory to read all the schemata. If the --schema file is in schema_dir, it will only be read once.",
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
        for stmt in sorted( dcatv3_ontology(args.schema_dir, args.schema) ):
            pprint.pprint(stmt)
            print()

    if args.validate:
        v = dhs_ontology.Validator( args.schema_dir, args.schema )
        while not sys.stdin.eof():
            jin  = json.load( sys.stdin )
            jout = validate( jin )
        json.dump(sys.stdout, jout, indent=4)
        sys.stdout.write("\n")

    if args.make_template:
        make_template(args.make_template, not args.noinstructions, schema_dir=args.schema_dir, schema=args.schema)

    if args.read_xlsx:
        for r in read_xlsx(args.read_xlsx):
            print(r)

    if args.writeschema:
        fmt = os.path.splitext(args.write)[1][1:].lower()
        if fmt=='json':
            fmt='json-ld'
        g2.serialize(destination=args.write, format=fmt)
