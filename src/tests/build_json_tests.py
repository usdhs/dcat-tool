import os
from os.path import abspath, dirname
from pyshacl import validate
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
import json
from datetime import datetime
import random

# =======================================
# Functions to generate test files for python unittest (Class)
# =======================================
# -- update the testSuiteDict (below) to add new test cases (each item builds a new test file and outputs to the tests dir)
# -- the validation_tests.py file needs the tests to be added to check eahc output file

# setup the schema file
SCHEMATA_DIR  = os.path.join(dirname(abspath( __file__ )) , "../../schemata")
COLLECT_TTL   = os.path.join(SCHEMATA_DIR, "dhs_collect.ttl")
s = Graph().parse(COLLECT_TTL)

ALL_QUERY = """
SELECT DISTINCT ?aProperty ?aMinCount ?aDataType
WHERE {
  {
  dhs:dataInventoryRecordShape sh:property ?aShapeName .
  ?aShapeName sh:path ?aProperty .
  OPTIONAL { ?aShapeName sh:minCount     ?aMinCount . }
  OPTIONAL { ?aShapeName sh:datatype     ?aDataType . }
  }
  UNION
  {
   dhs:characteristicsShape sh:property ?aShapeName .
  ?aShapeName sh:path ?aProperty .
  OPTIONAL { ?aShapeName sh:minCount     ?aMinCount . }
  OPTIONAL { ?aShapeName sh:datatype     ?aDataType . }
  }
}"""

# -- builds a useful data dictionary from the results of the SPARQL query --
def buildDataDict(k,v1,v2,v3):
    allNodesDict.update({k:{v1,v2,v3}})


allNodesDict = {}
allNodes = s.query(ALL_QUERY)
for row in allNodes:
    if(row[0].rfind('#')>0):
        start = row[0].rfind('#')
    else:
        start = row[0].rfind('/')
    rowDict = {"uri":str(row[0]),"min":str(row[1]),"type":str(row[2])}
    allNodesDict.update({row[0][start+1:]:rowDict})

testjson = {}


# -- build the context object for the head of the file --
def buildContext(jsonobj):
    contextHolder = {}
    contextobj = {}
    context = s.namespaces()
    for j in context:
        #print(j[0] + ' ... ' + str(j[1]))
        contextobj.update({j[0]:str(j[1])})
    contextHolder.update({"@context":contextobj})
    return contextHolder


# -- clean out unused namespaces --
def cleanContext(jsonobj):
    #print('the first node of the test json ++++++++++++++++++++++++++++++++++ ')
    ctx = jsonobj["@context"]
    #print(ctx)
    cleanContextItem(ctx,"foaf")
    cleanContextItem(ctx,"dt")
    cleanContextItem(ctx,"sh")
    cleanContextItem(ctx,"skos")
    cleanContextItem(ctx,"owl")

# -- a support function for cleaning names --
def cleanContextItem(jsonobj, itm):
    if itm in jsonobj:
        jsonobj.pop(itm)


def addAttributeToContext(jsonobj, attributeName, attributeObj):
    ctx = jsonobj["@context"]
    ctx.update({attributeName:attributeObj})



# --- build the required fields as a base --
def buildTestBase(testid, testDescription, jsonobj):
    thisday = datetime.today().strftime('%Y-%m-%d')
    testiduri = "https://dhs.gov/" + testid
    jsonobj.update({"@id":testiduri})
    jsonobj.update({"@type":"https://usdhs.github.io/dcat-tool/#DataInventoryRecord"})
    jsonobj.update({"http://purl.org/dc/terms/identifier":testid})
    jsonobj.update({"http://purl.org/dc/terms/title":testid})
    jsonobj.update({"http://purl.org/dc/terms/description":testDescription})
    dateobj = {}
    dateobj.update({"@type":"xsd:date"})
    dateobj.update({"@value":thisday})
    jsonobj.update({"http://purl.org/dc/terms/issued":dateobj})
    jsonobj.update({"http://resources.data.gov/resources/dcat-us/#accessLevel":"public"})
    jsonobj.update({"https://usdhs.github.io/dcat-tool/#dataCatalogRecordAccessLevel":"public"})
    jsonobj.update({"https://usdhs.github.io/dcat-tool/#component":"MGMT"})

    return jsonobj

# -- add nodes to the test file to test specific (or all) functionality -- 
# -- the nodename as 'all' will produce a 'full' test file with all nodes for testing --
def addTestNodes(nodeName, jsonobj, testValue = None):
    # -- look for the name and type and add it OR if 'all' then go through all the fields --
    if nodeName == 'all':
        # loop and add all elements in the allNodesDict
        # types that are not string need the type identified
        # print('inside ALL --- ' + str(len(allNodesDict)))
        for rw , vl in allNodesDict.items():
            if(vl["min"] == '0'):
                nodekey = allNodesDict.get(rw)
                dataTypekey = nodekey['type']
                if 'integer' in dataTypekey:
                    intobj = {}
                    intobj.update({'@type':dataTypekey})
                    rint = random.randrange(99)
                    intobj.update({'@value':rint})
                    jsonobj.update({nodekey["uri"]:intobj})        
                    #print('a int field! ----> ' + rw)
                elif 'boolean' in dataTypekey:
                    # if this is a 'ch-' type then 1. add the attribute type to the context, check to see if the object exists in the record for the class, add value to object
                    if('ch-' in nodekey["uri"]):
                        boolIdObj = {}
                        boolIdObj.update({'@id':nodekey["uri"]})
                        boolIdObj.update({'@type':dataTypekey})
                        addAttributeToContext(jsonobj,rw,boolIdObj)
                        #print('in boolean test... ' + rw)
                        if("https://usdhs.github.io/dcat-tool/#characteristics" in jsonobj):
                            charObj = jsonobj.get("https://usdhs.github.io/dcat-tool/#characteristics")
                            charObj.update({rw:"true"})
                            #print('just add the attribute and value')
                        else:
                            CharisteristicsObj = {}
                            CharisteristicsObj.update({'@type':'https://usdhs.github.io/dcat-tool/#Characteristics'})
                            CharisteristicsObj.update({rw:'true'})
                            jsonobj.update({"https://usdhs.github.io/dcat-tool/#characteristics":CharisteristicsObj})
                            #print('need a node!')
                    else:
                        boolobj = {}
                        boolobj.update({'@type':dataTypekey})
                        rbool = random.choice(['true','false'])
                        boolobj.update({'@value':rbool})
                        jsonobj.update({nodekey["uri"]:boolobj})        
                        #print('a bool field! ----> ' + rw)
                elif 'date' in dataTypekey:
                    dateobj = {}
                    dateobj.update({'@type':dataTypekey})
                    rdate = datetime.today().strftime('%Y-%m-%d')
                    dateobj.update({'@value':rdate})
                    jsonobj.update({nodekey["uri"]:dateobj})        
                    #print('a date field! ----> ' + rw)
                elif 'duration' in dataTypekey:
                    durationobj = {}
                    durationobj.update({'@type':dataTypekey})
                    durationobj.update({'@value':'P1Y'})
                    jsonobj.update({nodekey["uri"]:durationobj})
                elif 'anyURI' in dataTypekey:
                    uriobj = {}
                    uriobj.update({'@type':dataTypekey})
                    uriobj.update({'@value':'<https://ea.dhs.gov/mobius>'})
                    jsonobj.update({nodekey["uri"]:uriobj})
                elif 'string' in dataTypekey:
                    # -- handle UUI and Fisma --
                    #print('strings -- ' + rw)
                    if rw in ['primaryITInvestmentUII','fismaID','keyword','encryptionAlgorithm']:  
                        if rw == 'fismaID':
                            jsonobj.update({nodekey["uri"]:"FSA-00100-MAJ-00100"})
                        elif rw == 'keyword':
                            jsonobj.update({nodekey["uri"]:['test','dataset','Data Inventory Record']})
                        elif rw == 'primaryITInvestmentUII':
                            jsonobj.update({nodekey["uri"]:"010-999992220"})
                        else:
                            jsonobj.update({nodekey["uri"]:"3DES"})
                    #pass
                else:
                    if rw in ['owner','steward','custodian','contactPoint','publisher','creator','governance']:
                        if rw in ['publisher','creator','governance']:
                            #print('org only' + rw)
                            vcardOrgObj = {}
                            vcardOrgObj.update({'@type':'http://www.w3.org/2006/vcard/ns#Organization'})
                            vcardOrgObj.update({'http://www.w3.org/2006/vcard/ns#organization-name':'DHS'})
                            vcardOrgObj.update({'http://www.w3.org/2006/vcard/ns#organization-unit':'MGMT'})
                            jsonobj.update({nodekey["uri"]:vcardOrgObj})        
                        else:
                            vcardOrgObj = {}
                            vcardOrgObj.update({'@type':'http://www.w3.org/2006/vcard/ns#Individual'})
                            rName = random.choice(randomNames)
                            rOrg = random.choice(randomOrgs)
                            vcardOrgObj.update({'http://www.w3.org/2006/vcard/ns#organization-name':rOrg})
                            vcardOrgObj.update({'http://www.w3.org/2006/vcard/ns#fn':rName})
                            jsonobj.update({nodekey["uri"]:vcardOrgObj})
                            #print('******************** found a name!!! *****************' + rw) 
                    else:
                        #print('WIT??? -- '+ rw)
                        if rw == 'keyword':
                            jsonobj.update({nodekey["uri"]:['test','dataset','Data Inventory Record']})
                        elif rw in ['references','sharingAgreements','describedBy']:
                            jsonobj.update({nodekey["uri"]:'https://example.org/some/valuable/resource.html'})
                        elif rw in ['collectionAuthority','retentionAuthority','releaseAuthority']:
                            jsonobj.update({nodekey["uri"]:['Some Article of legal authority','or Executive Orders']})
                        elif rw in ['systemOfRecords']:
                            jsonobj.update({nodekey["uri"]:'https://example.org/a_SORN_entry.html'})
                        elif rw in ['recordsSchedule']:
                            jsonobj.update({nodekey["uri"]:['Pointer to a URL describing records management schedule','A description of the records management schedule']})
                        elif rw in ['conformsTo']:
                            jsonobj.update({nodekey["uri"]:'http://niem.github.io/reference/iepd/'})
                        elif rw in ['conformsFIPS']:
                            jsonobj.update({nodekey["uri"]:'https://www.nist.gov/publications/security-requirements-cryptographic-modules-includes-change-notices-1232002'})
                        elif rw in ['transliterationStandard']:
                            jsonobj.update({nodekey["uri"]:'https://www.iso.org/ics/01.140.10/x/'})
                        elif rw in ['sourceDatasets','destinationDatasets']:
                            jsonobj.update({nodekey["uri"]:['datasetA','datasetB','...']})
                        elif rw in ['describedByType']:
                            jsonobj.update({nodekey["uri"]:'application/json'})
                        elif rw in ['isPartOf']:
                            jsonobj.update({nodekey["uri"]:'Mobius'})
                        elif rw in ['spatial']:
                            jsonobj.update({nodekey["uri"]:'Downtown Washington, DC'})
                        elif rw in ['spatialResolutionInMeters']:
                            jsonobj.update({nodekey["uri"]:'5x5 meters'})
                        elif rw in ['temporal']:
                            jsonobj.update({nodekey["uri"]:'December, 2021'})
                        elif rw in ['temporalResolution']:
                            jsonobj.update({nodekey["uri"]:'P1M'})
                        elif rw in ['dataQualityAssessment']:
                            jsonobj.update({nodekey["uri"]:'This dataset has some gaps in crtical areas. Efforts are underway to remediate.'})
                        elif rw in ['format']:
                            jsonobj.update({nodekey["uri"]:'CSV'})
                        elif rw in ['vendor']:
                            jsonobj.update({nodekey["uri"]:['ECS','GeoManagement, Inc.']})
                        elif rw in ['license']:
                            jsonobj.update({nodekey["uri"]:'MIT'})
                        elif rw in ['accessRights']:
                            jsonobj.update({nodekey["uri"]:'public'})
                        elif rw in ['theme']:
                            jsonobj.update({nodekey["uri"]:['data management','data governance','data inventory']})
                        elif rw in ['functionalDataDomain']:
                            jsonobj.update({nodekey["uri"]:'IDII'})
                        elif rw in ['mediaType']:
                            jsonobj.update({nodekey["uri"]:'application/node'})
                        elif rw in ['mediaType']:
                            jsonobj.update({nodekey["uri"]:'application/node'})
                        elif rw in ['datasetClassification']:
                            jsonobj.update({nodekey["uri"]:'CUI'})
                        elif rw in ['hostingLocation']:
                            jsonobj.update({nodekey["uri"]:'CIRRUS'})
                        elif rw in ['characteristics']:
                            pass
                        else:
                            #print('Whats left? ----> ' + rw)
                            randomStringArray = randomString.split()
                            rstart = random.randrange(99)
                            strout = ' '.join(str(e) for e in randomStringArray[rstart:rstart+3])
                            #print(strout)
                            jsonobj.update({nodekey["uri"]:strout})

            
    else:
        #print('trying to add: ' + nodeName)
        if('ch-' in nodeName):
            nodekey = allNodesDict.get(nodeName)
            print('special treatment!')
            boolIdObj = {}
            boolIdObj.update({'@id':nodekey["uri"]})
            boolIdObj.update({'@type':nodekey["type"]})
            addAttributeToContext(jsonobj,nodeName,boolIdObj)
            #print('in boolean test... ' + rw)
            if("https://usdhs.github.io/dcat-tool/#characteristics" in jsonobj):
                charObj = jsonobj.get("https://usdhs.github.io/dcat-tool/#characteristics")
                charObj.update({nodeName:"true"})
                #print('just add the attribute and value')
            else:
                CharisteristicsObj = {}
                CharisteristicsObj.update({'@type':'https://usdhs.github.io/dcat-tool/#Characteristics'})
                CharisteristicsObj.update({nodeName:'true'})
                jsonobj.update({"https://usdhs.github.io/dcat-tool/#characteristics":CharisteristicsObj})
                #print('need a node!')
        else:        
            nodekey = allNodesDict.get(nodeName)
            jsonobj.update({nodekey["uri"]:testValue})

    return jsonobj

# -- lists and structures for random items in test files -- 
randomString = '''Kennedy used the phrase twice in his speech, including at the end, pronouncing the sentence with his Boston accent and reading from his note "ish bin ein Bearleener", 
which he had written out using English orthography to approximate the German pronunciation. He also used the classical Latin pronunciation of civis romanus sum, with the c pronounced [k] and the v as [w].
For decades, competing claims about the origins of the 'Ich bin ein Berliner' overshadowed the history of the speech. In 2008, historian Andreas Daum provided a comprehensive explanation, based on archival 
sources and interviews with contemporaries and witnesses. He highlighted the authorship of Kennedy himself and his 1962 speech in New Orleans as a precedent, and demonstrated that by straying from the prepared script in Berlin, Kennedy created the climax of an emotionally charged political performance, which became a hallmark of the Cold War epoch.
There is a widespread misconception that Kennedy accidentally said he was a Berliner, a German doughnut specialty. This is an urban legend, including the belief that the audience laughed at Kennedy's use of this expression.'''
randomNames = ['Abe Lincon','Mike Smythe','Anna Cole','Linda Mckay','Ron Johnson','John Jay','Kim Palsi','Gerry McDonald','Bill Bradly']
randomOrgs = ['CACI','ECS','Kinsley','PWC','United Nations','Booz Allen','Deloitte']


testSuiteDict = [
    {'id':'test-1','description':'test only required fields for DIP record','testObject':None,'node':None},
    {'id':'test-2','description':'test all fields for DIP record - a full record','testObject':None,'node':'all'},
    {'id':'test-3','description':'test keywords array in DIP record','testObject':['test','some','keywords'],'node':'keyword'},
    {'id':'test-4','description':'test keywords string','testObject':'test','node':'keyword'},
    {'id':'test-5','description':'test owner as string','testObject':'Mr Bingo','node':'owner'},
    {'id':'test-6','description':'test a characteristic','testObject':'true','node':'ch-pii'}
    ]

# -- the main function --
def buildTestSuite():
    for testcase in testSuiteDict:
        tjson = {}
        bjson = buildContext(tjson)
        cleanContext(bjson)
        if not testcase["node"]:
            #print('just build a base case')
            ojson = buildTestBase(testcase["id"], testcase["description"], bjson)
        elif testcase["node"] == 'all':
            #print('generate the whole')
            ojson = buildTestBase(testcase["id"], testcase["description"], bjson)
            ojson = addTestNodes('all', bjson)
        else:
            #ojson = addTestNodes('keyword', bjson, ['test','some','keywords'])
            ojson = buildTestBase(testcase["id"], testcase["description"], bjson)
            ojson = addTestNodes(testcase["node"], bjson, testcase["testObject"])
            #json_output = json.dumps(bjson, indent=4)
            #print(json_output)
        print('outputting test: ' + testcase["id"] + ' with node count: ' + str(len(ojson)))
        #print('len of base: ' + str(len(ojson)))
        json_output = json.dumps(ojson, indent=4)
        writeTestToFile(testcase["id"], json_output)

def writeTestToFile(fName, testObj):
    fileName = fName + '.json'
    with open(fileName, 'w') as outfile:
        outfile.write(testObj)


#print('inside ALL --- ' + str(allNodes))
buildTestSuite()
print('Done!')
