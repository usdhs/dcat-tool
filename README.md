# dcat-tool

[DCAT](https://www.w3.org/TR/vocab-dcat-3/) is the Data Catalog Vocabulary, a product of the World Wide Web
Consortium (WC3)'s Dataset Exchange Working Group.

This repo contains a tool that is intended to have the following
functionality:

1. Given an RDF schema, generate an Excel spreadsheet that can be used
   as a collection instrument for that schema.  (It's envisioned that
   the RDF Schema will be a subset of DCAT, because we don't want to
   collect with every attribute in the schema.)

   The excel spreadsheet should contain minimal validation.

2. Given a spreadsheet that's been filled out, parse the supplied data
   in the spreadsheet into its RDF representation.

3. Given an RDF representation of data elements, validate them, and
   create sensible error messages if validation fails. (We will use
   this to create web-forms that allow people to upload either RDF
   data or spreadsheets.)

# For additional Reference

This tool is based:
1. [W3C Data Catalog Vocabulary (DCAT) version 3 (draft recommendation)](https://www.w3.org/TR/vocab-dcat-3)
2. [W3C Data Exchange Working Group](https://www.w3.org/groups/wg/dx)
3. [DCAT-US Schema v1.1 (Project Open Data Metadata Schema)](https://resources.data.gov/resources/dcat-us/).
   See also the [POD schema documentation on github](https://github.com/GSA/resources.data.gov/tree/main/pages/schemas/dcat-us/v1.1/schema)

If you are unfamiliar with the W3C's Semantic Web standards, you may
find it useful to read these resources, in this order:

1. [W3C RDF 1.1 Primer](https://www.w3.org/TR/rdf11-primer/)
2. [RDF 1.1 Turtle --- The Terse RDF Triple Language](https://www.w3.org/TR/turtle/)
3. [rdflib documentation](https://rdflib.readthedocs.io/en/stable/)
4. [SHACL: Shapes Constraint Language, a W3C Recommendation](https://www.w3.org/TR/shacl/)
5. [OWL 2 Web Ontology Language Overview](https://www.w3.org/TR/owl2-overview/)

If you are looking for references that are not standards documents, try:

* [Learning SPARQL, 2nd Edition](https://www.oreilly.com/library/view/learning-sparql-2nd/9781449371449/)
* [Mustafa Jarrar's tutorial on SPARQL](http://www.jarrar.info/courses/WebData/Jarrar.LectureNotes.SPARQL.pdf)


## Related Concepts

Turtle
: An easy-to-author format for rendering RDF as text.

RDF/XML
: A rendering of RDF data into XML.

JSON-LD
: The JavaScript Object Notation Linked Data format, a specification
: based on JSON.
