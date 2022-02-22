import py.test
import os
import os.path
import rdflib
import glob
import sys
import tempfile
import openpyxl

from os.path import abspath,dirname,basename

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

SCHEMATA_DIR = os.path.join(dirname(dirname(dirname(abspath( __file__ )))) , "schemata")
TEST_DIR = dirname(abspath(__file__))

import dcat_tool
import easy_workbook
import dhs_ontology

def test_collect():
    DHS = rdflib.Namespace("http://github.com/usdhs/dcat-tool/0.1")
    g = rdflib.Graph()
    g.parse( dhs_ontology.COLLECT_TTL )

def test_excelGenerator():
    outdir = tempfile.TemporaryDirectory()
    outdir = "/tmp"             # for dev
    fname  = os.path.join(outdir, "inventory_tool.xlsx")
    g = easy_workbook.ExcelGenerator()
    g.add_markdown_sheet(name="Instructions", markdown=open(dcat_tool.INSTRUCTIONS).read(), versionNumber="1")
    g.add_columns_sheet("Inventory",
                        [easy_workbook.ColumnInfo(value="First Column", comment="Foo",
                                                  author="Author 1", width=50, typ='int', group='a'),
                         easy_workbook.ColumnInfo(value="Second Column", comment="Bar",
                                                  author="Author 2", width=50, typ='int', group='b')])
    g.save( fname )

def test_excelParser():
    # Make sure template is as expected
    wb = openpyxl.load_workbook( os.path.join(TEST_DIR, "test_template_clean.xlsx" ))

def test_excelIngest():
    r1 = dhs_ontology.read_xlsx(os.path.join(TEST_DIR, "test_template_clean.xlsx" ))
    assert len(r1) == 3

    r2 = dhs_ontology.read_xlsx(os.path.join(TEST_DIR, "test_template_error_uid.xlsx" ))
    assert len(r2) == 4
