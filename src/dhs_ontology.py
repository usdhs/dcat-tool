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
SELECT DISTINCT ?aProperty ?aTitle ?aPropertyComment ?aShapeComment ?aType ?aWidth ?aGroup ?aPropertyDefinedBy ?aPropertyLabel ?aMinCount ?aDataType
WHERE {
{
  dhs:dataInventoryRecordShape sh:property ?aShapeName .
  ?aShapeName sh:path ?aProperty .

  OPTIONAL { ?aProperty  rdfs:range      ?aType . }
  OPTIONAL { ?aProperty  rdfs:comment    ?aPropertyComment . }
  OPTIONAL { ?aProperty  rdfs:isDefinedBy    ?aPropertyDefinedBy . }
  OPTIONAL { ?aProperty  rdfs:label    ?aPropertyLabel . }
  OPTIONAL { ?aShapeName dhs:excelWidth  ?aWidth . }
  OPTIONAL { ?aShapeName dt:title        ?aTitle . }
  OPTIONAL { ?aShapeName dt:group        ?aGroup . }
  OPTIONAL { ?aShapeName rdfs:comment    ?aShapeComment . }
  OPTIONAL { ?aShapeName sh:minCount     ?aMinCount . }
  OPTIONAL { ?aShapeName sh:datatype     ?aDataType . }
  FILTER (!BOUND(?aPropertyLabel) || lang(?aPropertyLabel) = "" || lang(?aPropertyLabel) = "en" || lang(?aPropertyLabel) = "en-US")
  } 
  UNION 
  {
  dhs:characteristicsShape sh:property ?aShapeName .
  ?aShapeName sh:path ?aProperty .

  OPTIONAL { ?aProperty  rdfs:range      ?aType . }
  OPTIONAL { ?aProperty  rdfs:comment    ?aPropertyComment . }
  OPTIONAL { ?aProperty  rdfs:isDefinedBy    ?aPropertyDefinedBy . }
  OPTIONAL { ?aProperty  rdfs:label    ?aPropertyLabel . }
  OPTIONAL { ?aShapeName dhs:excelWidth  ?aWidth . }
  OPTIONAL { ?aShapeName dt:title        ?aTitle . }
  OPTIONAL { ?aShapeName dt:group        ?aGroup . }
  OPTIONAL { ?aShapeName rdfs:comment    ?aShapeComment . }
  OPTIONAL { ?aShapeName sh:minCount     ?aMinCount . }
  OPTIONAL { ?aShapeName sh:datatype     ?aDataType . }
  FILTER (!BOUND(?aPropertyLabel) || lang(?aPropertyLabel) = "" || lang(?aPropertyLabel) = "en" || lang(?aPropertyLabel) = "en-US")
  }
}
"""

def dhs_collect_graph(schema_file = COLLECT_TTL):
    g    = Graph()
    g.parse(schema_file, format='turtle')
    return g

def dcatv3_ontology(schemata_dir = SCHEMATA_DIR, schema_file = COLLECT_TTL):
    """Returns a graph of the DHS ontology for the data inventory program"""
    g    = Graph()
    seen = set()
    for fname in glob.glob( os.path.join(schemata_dir,"*.ttl")) + [schema_file]:
        if fname and fname not in seen:
            fname = os.path.abspath(fname)
            g.parse(fname, format='turtle')
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
        if d['aPropertyComment'].language not in ['en', None, '']:
            return True
    except (KeyError,AttributeError) as e:
        pass
    return False

def label_lang_check(labelIn):
    try:
        if labelIn.language in ['en']:
            return True
    except (KeyError,AttributeError) as e:
        pass
    return False

class ValidationFail( Exception ):
    pass

class Validator:
    def __init__(self, schemata_dir = SCHEMATA_DIR, schema_file = COLLECT_TTL, debug=False):
        self.debug = debug
        self.g = dcatv3_ontology(schemata_dir, schema_file)
        self.get_template_column_info_objs()
        self.seenIDs = set()
        self.rows    = []

    def clear(self):
        """Clear the seenIDs"""
        self.seenIDs.clear()

    def cleanGraph(self):
        """Return a graph with the namespace but none of the tripples"""
        g2 = Graph()
        # Copy over the namespaces from the triples we read to the graph we are producing
        for ns_prefix,namespace in self.g.namespaces():
            g2.bind(ns_prefix, namespace)
            #print("adding namespace prefix",ns_prefix,namespace)
        return g2

    def augmentGraph(self, g2, queryResult):
        # Now create the collection graph
        try:
            g2.add( (queryResult['aProperty'], RDFS.range,   queryResult['aType']) )
        except KeyError as e:
            pass

        try:
            g2.add( (queryResult['aProperty'], RDFS.comment,   queryResult['aComment']) )
        except KeyError as e:
            pass

    def get_query_dict(self):
        # creates a sorted list to output everything in the expected order
        baseDict = self.g.query( CI_QUERY )
        sortedDict = []
        groupList = []
        for q in baseDict:
            if q['aGroup'] not in groupList:
                groupList.append(q['aGroup'])
                #print('test it: ' + str(q['aGroup']))
        for k in groupList:
            for q in baseDict:
                if q['aGroup'] == k:
                    sortedDict.append(q)

        for r in sortedDict:
            d = r.asdict()
            if self.debug:
                print(d)
            if should_skip(d):
                if self.debug:
                    print(">> skip",d)
                continue
            yield d

    def get_descriptions(self):
        """Returns an iterator of tuples in the form (group, simplifed_property, description)"""
        simp = Simplifier(self.g)
        counter = 0
        for d in self.get_query_dict():
            group = d.get('aGroup', '')
            if(group == ''):
                continue
            comment = d.get('aShapeComment', d.get('aPropertyComment', ''))
            label = d.get('aPropertyLabel', '')
            definedByNS = d.get('aPropertyDefinedBy', '')
            requiredIn = d.get('aMinCount', '')
            required = "No"
            if(int(requiredIn) > 0):
                required = "Yes" 
            counter += 1
            #yield (group, simp.simplify(d['aProperty']), comment, label, definedByNS, required)
            yield (simp.simplify(group, namespace=False), simp.simplify(d['aProperty']), comment, label, definedByNS, required, simp.simplify(d.get('aType', DEFAULT_TYPE)), simp.simplify(d.get('aDataType', DEFAULT_TYPE)) )
        #print(str(counter))

    def get_namespace(self):
        """Returns an iterator of tuples in the form (group, simplifed_property, description)"""
        """Filters for the novel DHS-DCAT attribute namespace using a partial string defined below"""
        simp = Simplifier(self.g)
        namespaceStr = 'dcat-tool'
        counterb = 0
        for d in self.get_query_dict():
            definedByNS = d.get('aPropertyDefinedBy', '')
            if(namespaceStr in definedByNS):
                group = d.get('aGroup', '')
                if(group == ''):
                    continue
                comment = d.get('aShapeComment', d.get('aPropertyComment', ''))
                label = d.get('aPropertyLabel', '')
                definedByNS = d.get('aPropertyDefinedBy', '')
                requiredIn = d.get('aMinCount', '')
                required = "No"
                if(int(requiredIn) > 0):
                    required = "Yes"
                counterb += 1
                yield (group, simp.simplify(d['aProperty']), comment, label, definedByNS, required, simp.simplify(d.get('aType', DEFAULT_TYPE)), simp.simplify(d.get('aDataType', DEFAULT_TYPE)) )
        #print(str(counterb))

    def get_template_column_info_objs(self):
        # g2 is an output graph of the terms in the collection instrument
        g2 = self.cleanGraph()

        self.ci_objs = []
        simp = Simplifier(self.g)
        for d in self.get_query_dict():
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
                                           property = d['aProperty'],
                                           author = simp.simplify(d['aProperty']),
                                           width = int(d.get('aWidth',DEFAULT_WIDTH)),
                                           typ = simp.simplify(d.get('aDataType', DEFAULT_TYPE)),
                                           group = d.get('aGroup',''),
                                           )

            # Add the object to the column list and the graph
            self.ci_objs.append( obj )
            self.augmentGraph( g2, d )
        self.g2 = g2

    def validate(self, obj):
        """Check the dictionary (a loaded JSON object) """
        if not isinstance(obj,dict):
            raise ValidationFail(f'argument is type "{type(obj)}" and is not a JSON object or python dictionary')
        if 'dct:identifier' not in obj:
            raise ValidationFail('dct:identifier missing')
        return True

    def add_row(self, obj):
        """Validates a single object."""
        self.validate( obj )

        ident = obj['dct:identifier']
        if ident in self.seenIDs:
            raise ValidationFail(f'dct:identifier "{ident}" already seen')
        self.seenIDs.add(ident)
        self.rows.append( obj )

    # TODO: Implement shackl validation.
    # Make sure all mandatory fields are present
    # Make sure all fields have correct format


def validate_inventory_records( v, records ):
    ret = {}
    ret['response'] = 200       # looks good
    ret['records']  = []
    ret['messages'] = []
    ret['errors']   = []
    v.clear()
    for (num,record) in enumerate(records):
        ret['records'].append(record)
        try:
            v.add_row( record )
            ret['messages'].append('OK')
        except ValidationFail as e:
            ret['response'] = 409
            ret['errors'].append(num)
            ret['messages'].append(str(e))
    return ret

def read_xlsx(fname) :
    tr = template_reader.TemplateReader( fname )
    return list(tr.inventory_records())

def validate_xlsx( v, fname):
    return validate_inventory_records( v, read_xlsx( fname ) )
