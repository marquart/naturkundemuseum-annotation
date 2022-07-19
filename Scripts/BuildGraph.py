import os
from itertools import chain
from collections import defaultdict
import pickle

from igraph import Graph

from SemanticModels import SemanticEntity, SemanticProperty, SemanticData

def clean(txt):
    return txt.replace('\r\n', ' ').replace('\n', ' ').replace('‑', '').replace('-', '')


def visited(entity):
    return hasattr(entity, "component")

def DFS(entity, component_id, component_lst, lookup):
    entity.component = 0
    for e in entity.outgoing:
        neighbor = e.target
        if neighbor.type.startswith("E55 ") or visited(neighbor): continue
        DFS(neighbor, component_id, component_lst, lookup)
    for e in entity.incoming:
        neighbor = e.source
        if neighbor.type.startswith("E55 ") or visited(neighbor): continue
        DFS(neighbor, component_id, component_lst, lookup)
    entity.component = component_id
    component_lst.append(entity)
    
def find_components(entities):
    components = {}
    
    c_id = 1
    c_lst = []
    for entity in entities:
        if entity.type.startswith("E55 "): continue
        if not visited(entity):
            DFS(entity, c_id, c_lst, data)

            components[c_id] = sorted(c_lst, key=lambda e: len(e.outgoing), reverse=True)
            c_id += 1
            c_lst = []
    
    #assert len(chain.from_iterable(components)) == len(data["Entities"])
    processed = len(list(chain.from_iterable(components.values())))
    types = len([e for e in entities if e.type.startswith("E55 ")])
    assert processed+types == len(entities)
    #print(f"\n{data['Year'], data['Institution']}: Found {len(components)} Components for {processed} Entities (from {len(entities)} Entities without {types} Types)")

    for c_id, c_lst in components.items():
        #print(f"    Component {c_id}: {len(c_lst)} Entities, top: {c_lst[0].type} '{c_lst[0].string}' with {len(c_lst[0].outgoing)} targets")
        pass
    return components

def load_pickle(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data

def consoldiate_properties(property, queen, incoming=True):
    assert isinstance(property, SemanticProperty) and isinstance(queen, SemanticEntity)
    if incoming:
        property.target = queen
    else:
        property.source = queen
    return property

def consolidate_entities(entities, queens):
    only_one_entity_needed = ("E55 Type", "E78 Curated Holding", "E21 Person", "E53 Place", "E28 Conceptual Object")
    
    result = []
    matches = 0
    for entity in entities:
        if entity.type in only_one_entity_needed:
            entity_string = clean(entity.string).lower()
            if entity_string in queens[entity.type]:
                queen = queens[entity.type][entity_string]
                queen.incoming += [consoldiate_properties(p, queen, incoming=True) for p in entity.incoming]
                queen.outgoing += [consoldiate_properties(p, queen, incoming=False) for p in entity.outgoing]
                matches += 1
                #print(f"    Resolved {entity}({entity.id}) to {queen}({queen.id})")
            else:
                queens[entity.type][entity_string] = entity
                result.append(entity)
        else:
            result.append(entity)
            
    assert len(entities)-matches == len(result)
    
    print(f"{len(entities)} Entities resolved to {len(result)} Entities")
    return result, queens

def buildGraphWithYearsAsGlue():
    pickle_file = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    data = load_pickle(pickle_file)

    glue = defaultdict(dict)
    all_Entities = []
    all_Properties = []
    queens = defaultdict(dict) # consolidate over all documents
    
    len_glue = len(set([d["Year"] for d in data])) + len([d["Institution"] for d in data])
    for doc in data:
        entities = doc["Entities"].values()
        properties = doc["Properties"].values()
        
        entities, queens = consolidate_entities(entities, queens)
        print(f"Old properties: {len(properties)}, real properties: {sum([len(e.incoming) for e in entities])}")
        all_Entities += entities
        all_Properties += properties

        components = find_components(entities)
        glue[doc["Year"]][doc["Institution"]] = [c[0] for c in components.values()]
    
    assert len(all_Properties) == sum(len(e.incoming) for e in all_Entities) == sum(len(e.outgoing) for e in all_Entities)
    entity_node_lookup = {e:i for i,e in enumerate(all_Entities)}
    
    g = Graph(directed=True)
    g.add_vertices(len(all_Entities))
    g.add_edges([(entity_node_lookup[p.source], entity_node_lookup[p.target]) for p in all_Properties])
    
    
    g.vs["Label"] = [e.type for e in all_Entities] #+ ["E0 Metadata"]*len_glue
    g.vs["Text"] = [clean(e.string) for e in all_Entities] #+ [str(y) for y in year_node_lookup] + ins_strings
    
    print(f"\nBuild Graph with {len(g.vs)} nodes and {len(g.es)} edges")
    
    root = g.add_vertex(Label="Root: Jahresberichte", Text="Jahresberichte")
    for year, ins_co in glue.items():
        year_node = g.add_vertex(Label="E52 Time-Span", Text=str(year))
        g.add_edge(source=root, target=year_node.index)
        for ins, com in ins_co.items():
            ins_node = g.add_vertex(Label="E74 Group", Text=ins)
            g.add_edge(source=year_node, target=ins_node)
            for c in com:
                c_node = g.vs[entity_node_lookup[c]]
                g.add_edge(source=ins_node.index, target=c_node)
    print(f"Connected the graph, now with {len(g.vs)} nodes and {len(g.es)} edges")
    #print(g.vs[2535])
    
    g.save("C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/graph.graphml", format="graphml")
    
    
if __name__ == "__main__":

    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    data = SemanticData(pickle_file)
    entity_node_lookup = {e:i for i,e in enumerate(data.entities)}
    
    g = Graph(directed=True)
    g.add_vertices(len(data.entities))
    g.add_edges([(entity_node_lookup[p.source], entity_node_lookup[p.target]) for p in data.properties])
    
    
    g.vs["Label"] = [e.short_type for e in data.entities] #+ ["E0 Metadata"]*len_glue
    g.vs["Text"] = [e.string for e in data.entities] #+ [str(y) for y in year_node_lookup] + ins_strings
    g.vs["Color"] = [e.color for e in data.entities]
    
    assert len(g.vs)==len(data.entities) and len(g.es)==len(data.properties)
    savepath = "../Data/graph.graphml"
    g.save(savepath, format="graphml")
    print(f"\nBuild Graph with {len(g.vs)} nodes and {len(g.es)} edges")