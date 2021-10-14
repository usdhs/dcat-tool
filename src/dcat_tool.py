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
from rdflib import Dataset, Graph, URIRef, Literal, Namespace

#sys.path.append(os.path.dirname(__file__))


import easy_workbook

SCHEMATA_DIR = os.path.join(dirname(abspath( __file__ )) , "../schemata")
COLLECT_TTL  = os.path.join(SCHEMATA_DIR, "collect.ttl")
INSTRUCTIONS = os.path.join(dirname(abspath( __file__ )), "instructions.md")

# This should be folded into ctools schema package
class ExcelGenerator:
    def __init__(self, instructions=None):
        self.fields = []
        self.instructions = instructions

    def add(self,pair):
        """ add (field name, field type)"""
        self.fields.append(pair)

    def saveToExcel(self, fname):
        wb = easy_workbook.EasyWorkbook()
        wb.remove(wb.active)    # remove default sheet

        if self.instructions:
            ins = wb.create_sheet("Instructions")
            for (row,line) in enumerate(open(self.instructions),1):
                font = None
                if line.startswith("# "):
                    line = line[2:]
                    font = easy_workbook.H1
                if line.startswith("## "):
                    line = line[3:]
                    font = easy_workbook.H2
                if line.startswith("### "):
                    line = line[4:]
                    font = easy_workbook.H3
                ins.cell(row=row, column=1).value = line.strip()
                if font:
                    ins.cell(row=row, column=1).font = font

        inv = wb.create_sheet("Inventory")

        for (col,(name,typ)) in enumerate(self.fields,1):
            inv.cell(row=1, column=col).value = name
            inv.cell(row=1, column=col).alignment = easy_workbook.Alignment(textRotation=45)
        wb.save(fname)


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
    parser.add_argument("--print", help="Print the schema after it is read", action='store_true')
    parser.add_argument("--write", help="write the schema to the specified file")
    parser.add_argument("--makexls", help="specify the output filename of the Excel file to make for a collection schema")
    parser.add_argument("--extrafields", help="As a hack, specify a csv with DCAT attribute,datatype fields to add to the xls file")
    args = parser.parse_args()

    DHS = Namespace("http://github.com/usdhs/dcat-tool/0.1")
    print("DHS:",DHS)


    fnames = set()
    if args.schemadir:
        [fnames.add(fname) for fname in glob.glob( os.path.join(abspath(args.schemadir),"*.ttl")) ]
    if args.schema:
        fnames.add(abspath(args.schema))

    if not fnames:
        raise RuntimeError("No schema files specified")

    g = Graph()
    for fname in fnames:
        print("Reading",fname)
        g.parse(fname)

    if args.print:
        for stmt in g:
            pprint.pprint(stmt)

    if args.debug:
        for (s, p, o) in g.triples((None, None, None)):
            print(s,p,o)

    if args.makexls:
        print("DEBUG: Here are the columns that we want to collect, and the type for each:")
        for (s, p, o) in g.triples((None, None, DHS.CollectionRecord)):
            print(f"DEBUG: name: {s}")

    q = """
    SELECT ?nProperty ?nType
    WHERE {
     {?nProperty a dhs:DataInventoryRecord .}

      OPTIONAL { ?nProperty rdfs:range ?nType . }

      {?nProperty a owl:DatatypeProperty .}
      UNION
      {?nProperty a owl:ObjectProperty .}
      UNION
      {?nProperty a rdf:Property .}

    }
    """
    for r in g.query(q):
        print(r)
        print("--")

    if args.write:
        fmt = os.path.splitext(args.write)[1][1:].lower()
        if fmt=='json':
            fmt='json-ld'
        g.serialize(destination=args.write, format=fmt)
