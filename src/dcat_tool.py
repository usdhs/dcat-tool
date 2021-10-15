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
COLLECT_TTL  = os.path.join(SCHEMATA_DIR, "collect.ttl")
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


# This should be folded into ctools schema package
class ExcelGenerator:
    def __init__(self, instructions=None):
        self.fields = []
        self.instructions = instructions

    def add(self,info):
        """ add (dcat name, display name, help, width, field type)"""
        if len(info)!=5:
            raise ValueError(f"info={info}. Expected a list with 5 elements, got {len(info)}")
        self.fields.append(info)

    def saveToExcel(self, fname):
        wb = easy_workbook.EasyWorkbook()
        wb.windowWidth=800
        wb.windowHeight=1000
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

        for (col,(name,display,hlp,width,typ)) in enumerate(self.fields,1):
            from openpyxl.comments import Comment
            import openpyxl.utils
            # We tried making the comment string the description and the DCATv3 type is the comment "author", but that didn't work
            cell = inv.cell(row=1, column=col)
            cell.value = display
            cell.alignment = easy_workbook.Alignment(textRotation=45)
            cell.comment = Comment(f"{hlp} ({name})",name)
            inv.column_dimensions[ openpyxl.utils.get_column_letter( cell.col_idx) ].width   = int(width)
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
    parser.add_argument("--dump", help="Dump the triple store after everything it is read", action='store_true')
    parser.add_argument("--write", help="write the schema to the specified file")
    parser.add_argument("--makexlsx", help="specify the output filename of the Excel file to make for a collection schema")
    parser.add_argument("--extrafields", help="As a hack, specify a csv with DCAT attribute,datatype fields to add to the xls file")
    args = parser.parse_args()

    DHS = Namespace("http://github.com/usdhs/dcat-tool/0.1")
    print("DHS:",DHS)

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

    for r in g.query(CQUERY):
        print(r)
        print()
        print("---")

    if not query_result:
        print("ERROR. Query produced no output:",file=sys.stderr)
        print(CQUERY, file=sys.stderr)
        exit(1)

    if args.makexlsx:
        print("DEBUG: Here are the columns that we want to collect, and the type for each:")
        for (s, p, o) in g.triples((None, None, DHS.CollectionRecord)):
            print(f"DEBUG: name: {s}")
        eg = ExcelGenerator(instructions = INSTRUCTIONS)
        if args.extrafields:
            for line in open(args.extrafields):
                if line[0]=='#':
                    continue
                eg.add( line.split(","))
        eg.saveToExcel( args.makexlsx )

    if args.write:
        fmt = os.path.splitext(args.write)[1][1:].lower()
        if fmt=='json':
            fmt='json-ld'
        g.serialize(destination=args.write, format=fmt)
