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

def make_template_test():
    with tempfile.NamedTemporaryFile(suffix='.xlsx') as tf:
        os.unlink( tf.name )
        assert not os.path.exists( tf.name );
        dcat_tool.make_template( tf.name, True)
        assert os.path.exists( tf.name );
