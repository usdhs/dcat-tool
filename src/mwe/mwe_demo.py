#!/usr/bin/env demonstrate python namespaces

import rdflib
from rdflib import Dataset, Graph, URIRef, Literal, Namespace, BNode

if __name__=="__main__":
    g    = Graph()
    g.parse("mwe_schema.ttl")
    for r in g.query(
            """
            SELECT DISTINCT ?aSubject ?aPredicate ?anObject
            WHERE {
            ?aSubject ?aPredicate ?anObject
            }
            """):
        d = r.asdict()
        print(d['aSubject'],d['aPredicate'],d['anObject'])
