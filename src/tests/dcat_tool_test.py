import py.test
import os
import os.path
import rdflib
import glob
import sys
import tempfile

from os.path import abspath,dirname,basename

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

SCHEMATA_DIR = os.path.join(dirname(dirname(dirname(abspath( __file__ )))) , "schemata")

import dcat_tool
import easy_workbook

def test_collect():
    DHS = rdflib.Namespace("http://github.com/usdhs/dcat-tool/0.1")
    g = rdflib.Graph()
    g.parse( dcat_tool.COLLECT_TTL )

def test_excelGenerator():
    outdir = tempfile.TemporaryDirectory()
    outdir = "/tmp"             # for dev
    fname  = os.path.join(outdir, "inventory_tool.xlsx")
    g = easy_workbook.ExcelGenerator()
    g.add_markdown_sheet("Instructions", open(dcat_tool.INSTRUCTIONS).read())
    g.add_columns_sheet("Inventory",
                        [easy_workbook.ColumnInfo(value="First Column", comment="Foo", author="Author 1", width=50, typ='int'),
                         easy_workbook.ColumnInfo(value="Second Column", comment="Bar", author="Author 2", width=50, typ='int')])

    g.save( fname )

    # Now load the file and make sure that it has two sheets and instructions
