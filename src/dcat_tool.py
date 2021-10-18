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
from rdflib import Dataset, Graph, URIRef, Literal, Namespace

#sys.path.append(os.path.dirname(__file__))

import easy_workbook

SCHEMATA_DIR = os.path.join(dirname(abspath( __file__ )) , "../schemata")
COLLECT_TTL  = os.path.join(SCHEMATA_DIR, "dhs_collect.ttl")
INSTRUCTIONS = os.path.join(dirname(abspath( __file__ )), "instructions.md")

# CQUERY is the query to create the collection instrument
# ?aShapeName is the name of the blank nodes that are actually the column constraints in the schema.
CQUERY = """
SELECT ?aProperty ?aType ?aWidth
WHERE {
  dhs:dataInventoryRecord sh:property ?aShapeName .
  ?aShapeName sh:path ?aProperty .

  OPTIONAL { ?aProperty rdfs:range ?aType . }
  OPTIONAL { ?aShapeName dhs:excelWidth ?aWidth . }
}
"""


class Simplifier:
    def __init__(self, graph):
        self.graph = graph
    def simplify(self, token):
        for prefix,ns in self.graph.namespaces():
            if ns:
                if token.startswith(ns):
                    return prefix+":"+token[len(ns):]
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
    parser.add_argument("--extrafields", help="As a hack, specify a csv with DCAT attribute,datatype fields to add to the xls file")
    args = parser.parse_args()

    DHS = Namespace("http://github.com/usdhs/dcat-tool/0.1")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    print("DHS:",DHS)

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
        for stmt in sorted(g):
            pprint.pprint(stmt)
            print()

    # g2 is an output graph of the terms in the collection instrument
    simp = Simplifier(g)
    g2 = Graph()
    # Copy over the namespaces
    for ns_prefix,namespace in g.namespaces():
        print(f"bind({ns_prefix},{namespace})")
        g2.bind(ns_prefix, namespace)

    for r in g.query(CQUERY):
        d = r.asdict()
        (aProperty, aType, aWidth) = r
        print(simp.simplify(d.get('aProperty','')), d.get('aType','n/a'))
        if aProperty and aType:
            triple =(aProperty, RDFS.range, aType)
            #print("triple=",triple)
            g2.add(triple )

    #g2.serialize("foo.ttl",format="ttl")

    if args.extrafields:
        for line in open(args.extrafields):
            if line[0]=='#':
                continue
            ci = easy_workbook.ColumnInfo()
            (ci.name,ci.display,ci.hlp,ci.width,ci.typ) = line.split(",")
            ci_objs.append( ci )

    if args.makexlsx:
        eg = easy_workbook.ExcelGenerator()
        eg.add_markdown_sheet("Instructions", open(INSTRUCTIONS).read())
        eg.add_columns_sheet("Inventory", ci_objs)
        eg.save( args.makexlsx )

    if args.write:
        print(dir(g))
        exit(0)
        fmt = os.path.splitext(args.write)[1][1:].lower()
        if fmt=='json':
            fmt='json-ld'
        g.serialize(destination=args.write, format=fmt)
