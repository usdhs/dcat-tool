import py.test
import os
import os.path
import rdflib
import glob

from os.path import abspath,dirname,basename

SCHEMATA_DIR = os.path.join(dirname(dirname(abspath(__file__))))

def test_collect():
    assert os.path.exists(SCHEMATA_DIR)
    DHS = rdflib.Namespace("http://github.com/usdhs/dcat-tool/0.1")
    g = rdflib.Graph()
    for fn in glob.glob( os.path.join(SCHEMATA_DIR,"*.ttl") ):
        print(fn)
        g.parse(fn)
