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

import re

PROPERTY_RE = re.compile(r'([-a-zA-Z0-9]+:[-a-zA-Z0-9]+)')

class TemplateReader:
    def __init__(self, fn):
        self.fn = fn
        self.wb = openpyxl.load_workbook( fn )

    def is_inventory_worksheet(self, ws):
        """Return true if this is an inventory worksheet"""
        # Just read the first row
        for cell in next(ws.rows):
            try:
                if "dct:identifier" in cell.comment.text:
                    return True
            except AttributeError:
                pass
        return False

    def inventory_worksheets(self):
        return [ws for ws in self.wb if self.is_inventory_worksheet(ws)]

    def dcat_properties(self, ws):
        """For a given worksheet, return a set of pairs in the form (column #, dcat attribute)"""
        for cell in next(ws.rows):
            try:
                m = PROPERTY_RE.search(cell.comment.text)
            except AttributeError as e:
                continue
            if m:
                yield (cell.column, m.group(1))


    def process_worksheet(self, ws):
        pass
