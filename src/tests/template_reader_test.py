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

TEST_DIR = dirname(abspath(__file__))

import dcat_tool
import easy_workbook
import template_reader

def test_template_reader():
    tr = template_reader.TemplateReader( os.path.join(TEST_DIR, "test_template.xlsx" ) )
    assert len(tr.inventory_worksheets()) == 1
    ws = tr.inventory_worksheets()[0]

    cols = list(tr.dcat_properties(ws))
    assert(cols[0]==(1, 'dct:identifier'))
    assert(cols[1]==(2, 'dct:title'))
