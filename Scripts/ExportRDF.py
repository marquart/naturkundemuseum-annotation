
import os
from collections import defaultdict

import uuid

from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, DCTERMS

#from igraph import Graph as GraphML

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
                #("nq", "nquads")
    )
    for fileEnding, format in formats:
        destination = os.path.join(filepath, f"SemanticGraph.{fileEnding}")
        G.serialize(destination=destination, format=format)
        print(f"Saved graph to '{destination}'")

def makeValidURI(s):
    return s.replace(' ', '_')

def createEntityNodes(G, data):
    result = {}
    for e in data.entities:
        node = URIRef(generateUUID())
        G.add((node, RDF.type, CRM[makeValidURI(e.short_type)]))
        G.add((node, RDFS.label, Literal(e.string, lang="de")))
        G.add((node, CRM.P3, Literal(e.string, lang="de")))
        result[e] = node
    
    print(f"    Graph has {len(G)} triples after creating {len(result)} semantic entities")
    addedProperties = 0
    for e in data.entities:
        subj = result[e]
        for p in e.outgoing:
            obj = result[p.target]
            G.add((subj, CRM[makeValidURI(p.short_type)], obj))
            addedProperties += 1
    assert addedProperties == len(data.properties)
    print(f"    Graph has {len(G)} triples after connecting the semantic entities via {addedProperties} properties")
    return result

def createDocumentNodes(G, entityNodes, data):
    '''
    Eine Ausgabe ist ein E31 Document
    Eine Seite ist ein E31 Document (verbunden durch: Ausgabe-->P148 has component-->Page)
    Jede nicht-viruelle Entität ist verbunden mit Seite durch: 	Page-->P70 documents-->Entität
    '''
    BASE_DOC = URIRef("urn:nbn:de:kobv:11-d-6653534")
    G.add((BASE_DOC, RDF.type, CRM.E31))
    G.add((BASE_DOC, RDFS.label, Literal("Chronik der Friedrich-Wilhelms-Universität zu Berlin", lang="de")))

    URL_TABLE, ORIGINAL_PAGES, VOLUME_TABLE = get_URL_for_entity(None, filepath="../Data/URLS.json")
    lookup = defaultdict(dict) # txt_id:page:node
    lookup["base"][0] = BASE_DOC

    for txtData in data.texts:
        txt_id = txtData['Text_ID']
        year = txtData['Year']
        volume = URIRef(generateUUID())
        G.add((volume, RDF.type, CRM.E31))
        G.add((BASE_DOC, CRM.P148, volume))
        G.add((volume, DCTERMS.date, Literal(txtData['Year'])))

        citation = f"{build_citation(year, None, VOLUME_TABLE)[:-1]}, {txtData['Institution']}, {txtData['Page_Begin']}-{txtData['Page_End']}."
        G.add((volume, RDFS.label, Literal(citation, lang="de")))

        lookup[txt_id][0] = volume
        for pageNo, pageContent in txtData['Pages'].items():
            url = URL_TABLE[txt_id][str(pageNo)]
            original_page = ORIGINAL_PAGES[txt_id][str(pageNo)]
            citation = build_citation(year, original_page, VOLUME_TABLE)

            pageNode = URIRef(url)
            G.add((pageNode, RDFS.label, Literal(citation, lang="de")))
            G.add((pageNode, RDF.type, CRM.E31))
            G.add((pageNode, CRM.P190, Literal(pageContent.replace('\r',''), lang="de")))
            G.add((volume, CRM.P148, pageNode))


            lookup[txt_id][pageNo] = pageNode

    print(f"    Graph has {len(G)} triples after creating document nodes")
    for e, node in entityNodes.items():
        if e.page > 0:
            pageNode = lookup[e.txt_id][e.page]
            G.add((pageNode, CRM.P70, node))
    print(f"    Graph has {len(G)} triples after connecting semantic entities to document nodes")
    return lookup

CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm#")

if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    data = SemanticData(pickle_file)

    G = Graph(bind_namespaces="rdflib")
    G.bind('cidoc_crm', CRM)
    nodes = createEntityNodes(G, data)
    documents = createDocumentNodes(G, nodes, data)
    saveGraph(G, "../Data/RDF/")

    print(f"Graph has {len(list(G.subjects(unique=True)))} unique subjects (for {len(nodes)} semantic entities and {sum(len(v) for v in documents.values())} documents)")
    #grahpml = GraphML(directed=True)
