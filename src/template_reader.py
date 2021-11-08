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
        if not os.path.exists(fn):
            raise FileNotFoundError(fn)
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
            break
        return False

    def inventory_worksheets(self):
        return [ws for ws in self.wb if self.is_inventory_worksheet(ws)]

    def dcat_properties_for_row(self, row):
        """For a given worksheet, return a dictonary key=column#, value=dcat_attribute.
        The properties are learned from the comments of the first row.
        """
        props = {}
        seen  = set()
        for cell in row:
            try:
                m = PROPERTY_RE.search(cell.comment.text)
            except AttributeError as e:
                continue
            if m:
                name = m.group(1)
                if name in seen:
                    raise ValueError(f"{name} appears twice in the spreadsheet header.")
                props[cell.column] = name
        return props

    def dcat_properties(self, ws):
        return self.dcat_properties_for_row(next(ws.rows))

    def blank_row(self, row):
        for cell in row:
            if cell.value:
                return False
        return True

    def create_data_record(self, props, row):
        """Returns a record where the key=property and val=value"""
        ret = {}
        for cell in row:
            if cell.value:
                ret[ props[ cell.column ] ] = cell.value
        return ret

    def inventory_records(self):
        """Return all of the inventory records in the workbook."""
        props = None
        ret = []
        for ws in self.inventory_worksheets():
            # Get the properties, then each row that has data
            for row in ws.rows:
                # Get the props if we don't have it yet
                if props is None:
                    props = self.dcat_properties_for_row(row)
                    continue
                # Otherwise, if the row is not blank, get the data
                if not self.blank_row(row):
                    ret.append( self.create_data_record( props, row ) )
        return ret
