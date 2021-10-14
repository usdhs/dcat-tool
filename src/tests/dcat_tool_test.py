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
COLLECT_TTL  = os.path.join(SCHEMATA_DIR, "collect.ttl")

import dcat_tool

def test_collect():
    assert os.path.exists(SCHEMATA_DIR)
    DHS = rdflib.Namespace("http://github.com/usdhs/dcat-tool/0.1")
    g = rdflib.Graph()
    g.parse( COLLECT_TTL )

def test_excelGenerator():
    outdir = tempfile.TemporaryDirectory()
    outdir = "/tmp"             # for dev
    fname  = os.path.join(outdir, "inventory_tool.xlsx")
    g = dcat_tool.ExcelGenerator(instructions=dcat_tool.INSTRUCTIONS)
    g.add(("First Column",'int'))
    g.add(("Second Column",'string'))
    g.saveToExcel( fname )

    # Now load the file and make sure that it has two sheets and instructions
