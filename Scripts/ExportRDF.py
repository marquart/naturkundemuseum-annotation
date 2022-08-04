
import os
from collections import defaultdict

import uuid

from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, DCTERMS

from SemanticModels import SemanticEntity, SemanticProperty, SemanticData
from EntityURLResolver import get_URL_for_entity, build_citation

def generateUUID():
    return uuid.uuid1().urn

def saveGraph(G, filepath):
    formats = ( ("xml","pretty-xml"),
                ("ttl", "turtle"),
                ("jsonld", "json-ld"),
                ("nt", "nt11"),
                ("n3", "n3"),
    )
    for fileEnding, format in formats:
        G.serialize(destination=os.path.join(filepath, f"SemanticGraph.{fileEnding}"), format=format)

def makeValidURI(s):
    return s.replace(' ', '_')

def createEntityNodes(G, data):
    result = {}
    for e in data.entities:
        node = URIRef(generateUUID())
        G.add((node, RDFS.label, Literal(e.string, lang="de")))
        G.add((node, RDF.type, CRM[makeValidURI(e.short_type)]))
        result[e] = node
    
    addedProperty = 0
    for e in data.entities:
        subj = result[e]
        for p in e.outgoing:
            obj = result[p.target]
            G.add((subj, CRM[makeValidURI(p.short_type)], obj))
            addedProperty += 1
    assert addedProperty == len(data.properties)
    return result

def createDocumentNodes(G, entityNodes, data):
    '''
    Eine Ausgabe ist ein E31 Document
    Eine Seite ist ein E31 Document (verbunden durch: Ausgabe-->P148 has component-->Page)
    Jede nicht-viruelle Entität ist verbunden mit Seite durch: 	Page-->P70 documents-->Entität
    '''
    URL_TABLE, ORIGINAL_PAGES, VOLUME_TABLE = get_URL_for_entity(None, filepath="../Data/URLS.json")
    lookup = defaultdict(dict) # txt_id:page:node
    for txtData in data.texts:
        txt_id = txtData['Text_ID']
        year = txtData['Year']
        volume = URIRef(generateUUID())
        G.add((volume, RDF.type, CRM.E31))
        G.add((volume, DCTERMS.date, Literal(txtData['Year'])))

        citation = f"{build_citation(year, None, VOLUME_TABLE)[:-1]}, {txtData['Institution']}."
        G.add((volume, RDFS.label, Literal(citation, lang="de")))

        for pageNo, pageContent in txtData['Pages'].items():
            url = URL_TABLE[txt_id][str(pageNo)]
            original_page = ORIGINAL_PAGES[txt_id][str(pageNo)]
            citation = build_citation(year, original_page, VOLUME_TABLE)

            pageNode = URIRef(generateUUID())
            G.add((pageNode, RDFS.label, Literal(citation, lang="de")))
            G.add((pageNode, RDF.type, CRM.E31))
            G.add((volume, CRM.P148, pageNode))

            lookup[txt_id][pageNo] = pageNode

    for e, node in entityNodes.items():
        if e.page > 0:
            pageNode = lookup[e.txt_id][e.page]
            G.add((pageNode, CRM.P70, node))
    return lookup

CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm#")

if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    data = SemanticData(pickle_file)

    G = Graph()
    nodes = createEntityNodes(G, data)
    documents = createDocumentNodes(G, nodes, data)
    saveGraph(G, "../Data/RDF/")

