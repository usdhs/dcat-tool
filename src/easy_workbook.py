#!/usr/bin/env python3
#
# https://stackoverflow.com/questions/60824183/how-to-get-each-char-format-from-xlsx-cell-with-xlrd?
import datetime
import json
import os
import os.path
import re
import sqlite3
import sys
import time
import zipfile
import io
import logging
import numpy as np
import itertools
import statistics
import subprocess
import gc
import math
from collections import deque

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, PatternFill, Border, Side, Protection, Font, Fill, Color
from openpyxl.styles.borders import Border, Side, BORDER_THIN, BORDER_THICK
from openpyxl.comments import Comment
import openpyxl.styles.colors as colors

# https://htmlcolorcodes.com/

H1 = Font(bold=True, size=16)
H2 = Font(bold=True, size=14)
H3 = Font(bold=True, size=12)

BOLD        = Font(bold=True)
CENTERED    = Alignment(horizontal='center')
YELLOW_FILL = PatternFill(fill_type='solid', start_color='00ffff00', end_color='00ffff00')
PINK_FILL   = PatternFill(fill_type='solid', start_color='ffb6c1', end_color='ffb6c1')
LIGHT_GREEN_FILL  = PatternFill(fill_type='solid', start_color='EAFAF1', end_color='EAF8F1')

#PR_FILL = PatternFill(fill_type='solid', start_color='F4D03F', end_color='F4D03F')       # yellow
PR_FILL     = PatternFill(fill_type='solid', start_color='F4D03F')       # yellow
STATE1_FILL = PatternFill(fill_type='solid', start_color='F2F4F4')   # silver
STATE2_FILL = PatternFill(fill_type='solid', start_color='A9CCE3') # blue

def darker(openpyxl_fill):
    rgb = openpyxl_fill.start_color.rgb
    (r,g,b) = [int(s,16) for s in [rgb[0:2],rgb[2:4],rgb[4:6]]]
    r = max(r-1,0)
    g = max(g-1,0)
    b = max(b-1,0)
    color = f"{r:02X}{g:02X}{b:02X}"
    return PatternFill(fill_type='solid', start_color=color)

class EasyWorkbook(Workbook):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def clean(self):
        """Remove default 'Sheet' if exists"""
        if 'Sheet' in self:
            del self['Sheet']

    def format_rows(self,ws,*,min_row,max_row,column=None,skip_blank=True,min_col,max_col,fills=None,value_fills=None,stripe=False):
        """Apply colors to each row when column changes. If column is not specified, change every row."""
        if fills:
            fills = RingBuffer(fills)
            fill  = fills.next()
        prev_fill  = None
        prev_value = None
        make_darker = False
        for cellrow in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col):
            column_value = cellrow[column-min_col if column is not None else 0].value
            if skip_blank and column_value=='':
                continue

            make_darker  = not make_darker

            if not column_value:
                fill = None
            elif value_fills is not None and column_value in value_fills:
                fill = value_fills[column_value]
            elif column_value == prev_value:
                fill = prev_fill
                continue        #  don't change
            else:
                prev_fill   = fill       = fills.next()
                prev_value  = column_value
                make_darker = False

            #if make_darker and stripe:
            #    fill = darker(fill)

            for cell in cellrow:
                if fill:
                    cell.fill = fill

    def set_cell(ws,*,row,column,**kwargs):
        cell = ws.cell(row=row, column=column)
        for (key,value) in kwargs.items():
            setattr(cell, key, value)
