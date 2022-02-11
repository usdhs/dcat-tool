# DIP Test Excel pop
import openpyxl
import json
import os
import os.path
from os.path import abspath, dirname


# read in the emply template using openpyxl
# get the directory for 'samples' --
SAMPLES_DIR  = os.path.join(dirname(abspath( __file__ )) , "../../docs/samples")
EXCEL_TEMPLATE   = os.path.join(SAMPLES_DIR, "DIP_Excel_Template.xlsx")

workbook = openpyxl.load_workbook(EXCEL_TEMPLATE)
#workbook = openpyxl.load_workbook('DIP_Excel_Template.xlsx')
ws = workbook["Inventory"]
column_list = [cell.value for cell in ws[1]]
#print(column_list)

def findExcelColumn(fieldName):
    for cell in ws[1]:
        if(cell.value == fieldName):
            #print(cell.value)
            return cell.column


# readin a test file (later this will generate from build_test)
with open('test-3.json') as json_file:
    parsed = json.load(json_file)

for o, v in parsed.items():
    if(o.rfind('#')>0):
        start = o.rfind('#')
    else:
        start = o.rfind('/')
    term = o[start+1:]
    if term == 'identifier':
        term = 'unique identifier'
    colNo = findExcelColumn(term)
    # -- check for values that need stripping -- 
    if not term.startswith('@'):
        #print(term)
        #print(findExcelColumn(term))
        #print(v)
        if not isinstance(v, str):
            if isinstance(v, list):
                print('its a list!')
                pvalue = ",".join(v)
            else:
                pvalue = v["@value"]
            ws.cell(row=2, column=colNo).value = pvalue
        else:
            ws.cell(row=2, column=colNo).value = v


workbook.save("test_excel-1.xlsx")

