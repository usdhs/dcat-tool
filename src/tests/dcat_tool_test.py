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

def test_collect():
    DHS = rdflib.Namespace("http://github.com/usdhs/dcat-tool/0.1")
    g = rdflib.Graph()
    g.parse( dcat_tool.COLLECT_TTL )

def test_excelGenerator():
    outdir = tempfile.TemporaryDirectory()
    outdir = "/tmp"             # for dev
    fname  = os.path.join(outdir, "inventory_tool.xlsx")
    g = dcat_tool.ExcelGenerator(instructions=dcat_tool.INSTRUCTIONS)
    g.add(("First Column",'','',50,'int'))
    g.add(("Second Column",'','',50,'string'))
    g.saveToExcel( fname )

    # Now load the file and make sure that it has two sheets and instructions
