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
import rdflib
from rdflib import Dataset, Graph, URIRef, Literal, Namespace
import openpyxl

class TemplateReader:
    def __init__(self, fn):
        self.fn = fn
        self.wb = openpyxl.load_workbook( fn )

    def is_inventory_worksheet(self, ws):
        """Return true if this is an inventory worksheet"""
        for row in ws.rows:
            for cell in row:
                try:
                    if "dct:identifier" in cell.comment.text:
                        return True
                except AttributeError:
                    pass
            break                   # only look at the first row
        return False

    def inventory_worksheets(self):
        return [ws for ws in self.wb if self.is_inventory_worksheet(ws)]
