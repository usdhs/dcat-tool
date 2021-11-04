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

import template_reader
import easy_workbook

DHS           = Namespace("http://github.com/usdhs/dcat-tool/0.1")
XSD           = Namespace("http://www.w3.org/2001/XMLSchema#")
RDFS          = Namespace("http://www.w3.org/2000/01/rdf-schema#")

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

  OPTIONAL { ?aProperty  rdfs:range      ?aType . }
  OPTIONAL { ?aProperty  rdfs:comment    ?aPropertyComment . }
  OPTIONAL { ?aShapeName dhs:excelWidth  ?aWidth . }
  OPTIONAL { ?aShapeName dt:title        ?aTitle . }
  OPTIONAL { ?aShapeName dt:group        ?aGroup . }
  OPTIONAL { ?aShapeName rdfs:comment    ?aShapeComment . }
  OPTIONAL { ?aShareName sh:minCount     ?aMinCount . }
}
"""

def dcatv3_ontology(schemata_dir = SCHEMATA_DIR, schema_file = COLLECT_TTL):
    """Returns a graph of the DHS ontology for the data inventory program"""
    g    = Graph()
    seen = set()
    for fname in glob.glob( os.path.join(schemata_dir,"*.ttl")) + [schema_file]:
        if fname and fname not in seen:
            fname = os.path.abspath(fname)
            g.parse(fname)
            seen.add(fname)
    if not seen:
        raise RuntimeError("No schema files specified")
    return g

class Simplifier:
    def __init__(self, graph):
        self.graph = graph
    def simplify(self, token, namespace=True):
        for prefix,ns in self.graph.namespaces():
            if ns:
                if token.startswith(ns):
                    if namespace:
                        return prefix+":"+token[len(ns):]
                    else:
                        return token[len(ns):]
        return token

def should_skip(d):
    """Skip query responses that are not in English"""
    # Skip property comments that are not in english
    try:
        if d['aPropertyComment'].language != 'en':
            return True
    except (KeyError,AttributeError) as e:
        pass
    return False

def get_template_column_info_objs(g, query, debug=False):
    # g2 is an output graph of the terms in the collection instrument

    g2 = Graph()

    # Copy over the namespaces from the triples we read to the graph we are producing
    for ns_prefix,namespace in g.namespaces():
        g2.bind(ns_prefix, namespace)

    ci_objs = []
    simp = Simplifier(g)
    for r in g.query( query ):
        d = r.asdict()

        if debug:
            print(d)

        if should_skip(d):
            if debug:
                print(">> skip")
            continue

        try:
            title = d['aTitle']
        except KeyError:
            title = simp.simplify(d['aProperty'], namespace=False)

        # For the comment, grab the shape comment if it is present. otherwise, grab the property comment.
        # The comment goes into the tooltip for the column
        comment = d.get('aShapeComment', d.get('aPropertyComment', ''))
        if not comment:
            print("Need description for",d['aProperty'])

        obj = easy_workbook.ColumnInfo(value = title, # what is displayed in cell
                                       comment = title + ":\n" + comment,
                                       author = simp.simplify(d['aProperty']),
                                       width = int(d.get('aWidth',DEFAULT_WIDTH)),
                                       typ = simp.simplify(d.get('aType', DEFAULT_TYPE)),
                                       group = d.get('aGroup',''),
                                       )

        # Add the object to the column list
        ci_objs.append( obj )

        # Now create the collection graph
        try:
            g2.add( (d['aProperty'], RDFS.range,   d['aType']) )
        except KeyError as e:
            pass

        try:
            g2.add( (d['aProperty'], RDFS.comment,   d['aComment']) )
        except KeyError as e:
            pass
    return (g2, ci_objs)

class Validator:
    def __init__(self, schemata_dir = SCHEMATA_DIR, schema_file = COLLECT_TTL):
        self.g = dcatv3_ontology(schemata_dir, schema_file)
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
