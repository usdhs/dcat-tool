"""
Validate data inventory records.
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
import template_reader

RDFS          = Namespace("http://www.w3.org/2000/01/rdf-schema#")
XSD           = Namespace("http://www.w3.org/2001/XMLSchema#")
DHS           = Namespace("http://github.com/usdhs/dcat-tool/0.1")
SCHEMATA_DIR  = os.path.join(dirname(abspath( __file__ )) , "../schemata")
COLLECT_TTL   = os.path.join(SCHEMATA_DIR, "dhs_collect.ttl")
DEFAULT_WIDTH = 15              # Excel spreadsheet default width
DEFAULT_TYPE  = XSD.string

"""
CI_QUERY is the query to create the collection instrument
It finds all of the properties that are within the dhs:dataInventoryRecord and
then does a join with OPTIONAL on several other objects we would like to extract.on several

?aShapeName is the name of the blank nodes that are actually the column constraints in the schema.
?aTitle is the title in the excel spreadsheet
?aGroup is the group within the excel spreadsheet
"""

CI_QUERY = """
SELECT DISTINCT ?aProperty ?aTitle ?aPropertyComment ?aShapeComment ?aType ?aWidth ?aGroup
WHERE {
  dhs:dataInventoryRecord sh:property ?aShapeName .
  ?aShapeName sh:path ?aProperty .

  OPTIONAL { ?aProperty  rdfs:range     ?aType . }
  OPTIONAL { ?aProperty  rdfs:comment   ?aPropertyComment . }
  OPTIONAL { ?aShapeName dhs:excelWidth ?aWidth . }
  OPTIONAL { ?aShapeName dt:title  ?aTitle . }
  OPTIONAL { ?aShapeName dt:group  ?aGroup . }
  OPTIONAL { ?aShapeName rdfs:comment    ?aShapeComment . }
}
"""

def dcatv3_ontology(schemadir, schema_files):
    g    = Graph()
    seen = set()
    for fname in glob.glob( os.path.join(args.schemadir,"*.ttl")) + [args.schema]:
        if fname and fname not in seen:
            fname = os.path.abspath(fname)
            g.parse(fname)
            seen.add(fname)
    if not seen:
        raise RuntimeError("No schema files specified")
    return g



class Validator:
    def __init__(self, schemadir, schema):
        self.g = dcatv3_ontology(args.schemadir, args.schema)
        (self.g2, self.ci_objs) = get_template_column_info_objs(g, CI_QUERY)
        self.seenIDs = set()


    def add_row(self, row):
        """Validates a single object."""
        if 'dct:identifier' not in row:
            raise ValueError('dct:identifier missing')

        ident = row['dct:identifier']
        if ident in self.seenIDs:
            raise KeyError('dct:identifier already seen')
        self.seenIDs.add(ident)
        jout['input'] = jin['input']

    # TODO: Implement shackl validation.
    # Make sure all mandatory fields are present
    # Make sure all fields have correct format
