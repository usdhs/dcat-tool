import py.test
import os
import os.path
import rdflib

from os.path import abspath,dirname,basename

COLLECT_TTL = os.path.join(dirname(dirname(abspath(__file__))), "collect.ttl")

def test_collect():
    assert os.path.exists(COLLECT_TTL)
    DHS = rdflib.Namespace("http://github.com/usdhs/dcat-tool/0.1")
    g = rdflib.Graph()
    g.parse(COLLECT_TTL)
