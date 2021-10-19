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
import rdflib
from rdflib import Dataset, Graph, URIRef, Literal, Namespace

#sys.path.append(os.path.dirname(__file__))

import easy_workbook

SCHEMATA_DIR = os.path.join(dirname(abspath( __file__ )) , "../schemata")
COLLECT_TTL  = os.path.join(SCHEMATA_DIR, "dhs_collect.ttl")
INSTRUCTIONS = os.path.join(dirname(abspath( __file__ )), "instructions.md")
DEFAULT_WIDTH = 15              # Excel spreadsheet default width

# CQUERY is the query to create the collection instrument
# ?aShapeName is the name of the blank nodes that are actually the column constraints in the schema.
CQUERY = """
SELECT DISTINCT ?aProperty ?aTitle ?aComment ?aType ?aWidth ?aGroup
WHERE {
  dhs:dataInventoryRecord sh:property ?aShapeName .
  ?aShapeName sh:path ?aProperty .

  OPTIONAL { ?aProperty  rdfs:range ?aType . }
  OPTIONAL { ?aShapeName dhs:excelWidth ?aWidth . }
  OPTIONAL { ?aProperty  rdfs:comment   ?aComment . }
  OPTIONAL { ?aShapeName dt:title  ?aTitle . }
  OPTIONAL { ?aShapeName dt:group  ?aGroup . }
}
"""

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

if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Use a DCAT schema to produce capture instruments and APIs.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--schemadir",
                        help="specify the directory to read all the schemata. If the --schema file is in schemadir, it will only be read once.", default=SCHEMATA_DIR)
    parser.add_argument("--schema",
                        help="specify the collection schema file in Turtle, RDF/XML or RDF/JSON",
                        default=COLLECT_TTL)
    parser.add_argument("--debug", help="Enable debugging", action='store_true')
    parser.add_argument("--dump", help="Dump the triple store after everything it is read", action='store_true')
    parser.add_argument("--write", help="write the schema to the specified file")
    parser.add_argument("--makexlsx", help="specify the output filename of the Excel file to make for a collection schema")
    parser.add_argument("--noinstructions", help="Do not generate instructions. Mostly for debugging.", action='store_true')
    args = parser.parse_args()

    DHS = Namespace("http://github.com/usdhs/dcat-tool/0.1")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    XSD  = Namespace("http://www.w3.org/2001/XMLSchema#")

    DEFAULT_TYPE = XSD.string

    ci_objs = []
    g = Graph()
    seen   = set()
    for fname in glob.glob( os.path.join(args.schemadir,"*.ttl")) + [args.schema]:
        if fname and fname not in seen:
            fname = os.path.abspath(fname)
            g.parse(fname)
            seen.add(fname)

    if not seen:
        raise RuntimeError("No schema files specified")

    if args.dump:
        print("Dumping triple store:\n")
        for stmt in sorted(g):
            pprint.pprint(stmt)
            print()

    # g2 is an output graph of the terms in the collection instrument
    g2 = Graph()

    # Copy over the namespaces from the triples we read to the graph we are producing
    for ns_prefix,namespace in g.namespaces():
        g2.bind(ns_prefix, namespace)

    simp = Simplifier(g)
    for r in g.query(CQUERY):
        d = r.asdict()
        skip = False
        try:
            if d['aComment'].language != 'en':
                skip = True
        except (KeyError,AttributeError) as e:
            pass
        if skip:
            continue

        try:
            title = d['aTitle']
        except KeyError:
            title = simp.simplify(d['aProperty'], namespace=False)

        obj = easy_workbook.ColumnInfo(value = title, # what is displayed in cell
                                       comment = title + ":\n" + d.get('aComment',''),
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


    if args.makexlsx:
        eg = easy_workbook.ExcelGenerator()
        if not args.noinstructions:
            eg.add_markdown_sheet("Instructions", open(INSTRUCTIONS).read())
        eg.add_columns_sheet("Inventory", ci_objs)
        eg.save( args.makexlsx )

    if args.write:
        fmt = os.path.splitext(args.write)[1][1:].lower()
        if fmt=='json':
            fmt='json-ld'
        g2.serialize(destination=args.write, format=fmt)
