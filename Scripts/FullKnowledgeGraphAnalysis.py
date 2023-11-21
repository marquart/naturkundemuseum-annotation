from collections import defaultdict
import itertools

from GlobalConsolidate import generalize_global_person
from SemanticModels import SemanticEntity, SemanticProperty, SemanticData

from igraph import Graph

class Node(object):
    def __init__(self, e, label=None) -> None:
        self.e = e
        if label: self.label = label
        else: self.label = self.e.string

def objects_from_sumatra(data):
    sumatra = None
    for e in data.entities:
        if e.short_type == "E41" and e.search_string == "sumatra":
            sumatra = e
            break

    assert sumatra
    for e in sumatra.incoming(): pass

def collection_place_graph(data, search_string):
    def get_indexes(edge):
        source = nodes.index(edge[0])
        target = nodes.index(edge[1])
        return (source, target)
    
    appellation = None
    for e in data.entities:
        if e.short_type == "E41" and search_string in e.search_string:
            appellation = e
            break
    assert appellation

    searchstring_entity = {}
    g = Graph(directed=True)
    last_collection = None
    nodes = []
    edges = []
    for collection in sorted(list(appellation.incoming_entities()), key=lambda x:x.year):
        if collection.short_type == "E78" and collection not in nodes: #idx_entity:
            nodes.append(collection) #add_node(person)
            places = []

            for acquisition in collection.incoming_entities():
                if acquisition.short_type in ("E8","E96"):
                    for obj in acquisition.outgoing_entities():
                        if obj.short_type in ("E19", "E20"):
                            for place in obj.outgoing_entities():
                                if place.short_type == "E53": places.append(place)

            for place in places:
                name = place.search_string
                if name in searchstring_entity:
                    edges.append((collection, searchstring_entity[name]))
                else:
                    nodes.append(place)
                    searchstring_entity[name] = place
                    edges.append((collection, place))
            if last_collection is not None:
                edges.append((last_collection, collection)) #g.add_edges(((last_person, idx_entity[person]),))
            else: print(f"No Predecessor Year for {collection}")
            last_collection = collection

    #sorted_nodes = sorted(idx_entity, key=lambda x:idx_entity[x])
    g.add_vertices(len(nodes))
    g.add_edges([get_indexes(pair) for pair in reversed(edges)])
    g.vs["Label"] = [f"{e.string} ({e.year})" if e.short_type == "E78" else e.string for e in nodes]
    g.vs["Color"] = [e.color for e in nodes]
    g.vs["r"] = [int(color[1:3], 16) for color in g.vs["Color"]]
    g.vs["g"] = [int(color[3:5], 16) for color in g.vs["Color"]]
    g.vs["b"] = [int(color[5:7], 16) for color in g.vs["Color"]]
    g.vs["a"] = [1.0  for color in g.vs["Color"]]
    
    savepath = f"../../Temp_Visualizations/GraphMLs/{search_string}_places.graphml"
    g.save(savepath, format="graphml")
    print(f"\nBuild Graph with {len(g.vs)} nodes and {len(g.es)} edges")

    
def place_person_graph(data, search_string):
    def get_indexes(edge):
        if edge[0] in middleman_copies and middleman_copies[edge[0]]: source = middleman_copies[edge[0]].pop()
        else: source = nodes.index(edge[0])
        if edge[1] in middleman_copies and middleman_copies[edge[1]]: target = middleman_copies[edge[1]].pop()
        else: target = nodes.index(edge[1])
        return (source, target)
    
    appellation = None
    for e in data.entities:
        if e.short_type == "E41" and e.search_string == search_string:
            appellation = e
            break
    assert appellation

    searchstring_entity = {}
    g = Graph(directed=True)
    last_place = None
    middleman_copies = defaultdict(list) # entity: [..indexes in nodes which are occupied by entity]
    nodes = []
    edges = []
    for place in sorted(list(appellation.incoming_entities()), key=lambda x:x.year):
        if place not in nodes: #idx_entity:
            nodes.append(place) #add_node(person)
            for obj in place.incoming_entities():
                if obj.short_type in ("E19", "E20"):
                    concept = None
                    persons = []
                    for pot_concept in obj.outgoing_entities():
                        if pot_concept.short_type == "E28":
                            concept = pot_concept
                    for acquisition in obj.incoming_entities():
                        if acquisition.short_type in ("E8","E96"):
                            for relation in acquisition.outgoing:
                                if not concept and relation.short_type == "P22": concept = relation.target
                                if relation.short_type == "P23": persons.append(relation.target)
                    if concept:
                        if concept in nodes: middleman_copies[concept].append(len(nodes))
                        nodes.append(concept)
                        edges.append((place, concept))
                        for person in persons:
                            name = generalize_global_person(person)
                            if name in searchstring_entity:
                                edges.append((concept, searchstring_entity[name]))
                            else:
                                nodes.append(person)
                                searchstring_entity[name] = person
                                edges.append((concept, person))
                            if middleman_copies[concept]: middleman_copies[concept].append(middleman_copies[concept][-1])
                    else:
                        for person in persons:
                            name = generalize_global_person(person)
                            if name in searchstring_entity:
                                edges.append((place, searchstring_entity[name]))
                            else:
                                nodes.append(person)
                                searchstring_entity[name] = person
                                edges.append((place, person))
            if last_place is not None:
                edges.append((last_place, place)) #g.add_edges(((last_person, idx_entity[person]),))
            else: print(f"No Predecessor Year for {place}")
            last_place = place

    #sorted_nodes = sorted(idx_entity, key=lambda x:idx_entity[x])
    g.add_vertices(len(nodes))
    g.add_edges([get_indexes(pair) for pair in reversed(edges)])
    g.vs["Label"] = [f"{e.string} ({e.year})" if e.short_type == "E53" else e.string for e in nodes]
    g.vs["Color"] = [e.color if e.short_type != "E78" else "#06b67eaa" for e in nodes]
    g.vs["r"] = [int(color[1:3], 16) for color in g.vs["Color"]]
    g.vs["g"] = [int(color[3:5], 16) for color in g.vs["Color"]]
    g.vs["b"] = [int(color[5:7], 16) for color in g.vs["Color"]]
    g.vs["a"] = [1.0  for color in g.vs["Color"]]
    
    savepath = f"../../Temp_Visualizations/GraphMLs/{search_string}_persons.graphml"
    g.save(savepath, format="graphml")
    print(f"\nBuild Graph with {len(g.vs)} nodes and {len(g.es)} edges")

def collector_career_graph(data, search_string):
    def add_node(entity):
        g.add_vertices(1)
        id_ = next(ID_Generator)
        assert id_ == len(g.vs)-1
        idx_entity[entity] = id_
        return id_

    ID_Generator = itertools.count()
    appellation = None
    for e in data.entities:
        if e.short_type == "E41" and e.search_string == search_string:
            appellation = e
            break
    assert appellation

    searchstring_entity = {}
    idx_entity = {}
    g = Graph(directed=True)
    last_person = None
    nodes = []
    edges = []
    for person in sorted(list(appellation.incoming_entities()), key=lambda x:x.year):
        if person not in nodes: #idx_entity:
            nodes.append(person) #add_node(person)
            for acquisition in person.incoming_entities():
                processed = False
                if acquisition.short_type in ("E8","E96"):
                    for obj in acquisition.outgoing_entities():
                        if obj.short_type in ("E19", "E20"):
                            concept = None
                            places = []
                            for x in obj.outgoing_entities():
                                if x.short_type == "E28":
                                    concept = x
                                elif x.short_type == "E53":
                                    places.append(x)
                            processed = True
                            if concept:
                                nodes.append(concept) # concept_id = add_node(concept)
                                edges.append((person, concept)) # g.add_edges(((idx_entity[person], concept_id),))
                            else:
                                concept = obj
                                nodes.append(concept) #concept_id = add_node(concept)
                                edges.append((person, concept)) # g.add_edges(((idx_entity[person], concept_id),))
                            for place in places:
                                if place.search_string in searchstring_entity:
                                    e = searchstring_entity[place.search_string]
                                    assert e in nodes
                                    edges.append((concept, e)) #g.add_edges(((idx_entity[concept], idx_entity[e]),))
                                else:
                                    assert place not in nodes #idx_entity
                                    nodes.append(place) #place_id = add_node(place)
                                    searchstring_entity[place.search_string] = place
                                    edges.append((concept, place)) # g.add_edges(((idx_entity[concept], place_id),))
                    if not processed:
                        for holding in acquisition.outgoing_entities():
                            if holding.short_type == "E78":
                                nodes.append(holding)
                                edges.append((person, holding))
            if last_person is not None:
                edges.append((last_person, person)) #g.add_edges(((last_person, idx_entity[person]),))
            else: print(f"No Predecessor Year for {person}")
            last_person = person

    #sorted_nodes = sorted(idx_entity, key=lambda x:idx_entity[x])
    g.add_vertices(len(nodes))
    g.add_edges([(nodes.index(pair[0]), nodes.index(pair[1])) for pair in edges])
    g.vs["Label"] = [f"{e.string} ({e.year})" if e.short_type == "E21" else e.string for e in nodes]
    g.vs["Color"] = [e.color if e.short_type != "E78" else "#06b67eaa" for e in nodes]
    g.vs["r"] = [int(color[1:3], 16) for color in g.vs["Color"]]
    g.vs["g"] = [int(color[3:5], 16) for color in g.vs["Color"]]
    g.vs["b"] = [int(color[5:7], 16) for color in g.vs["Color"]]
    g.vs["a"] = [1.0  for color in g.vs["Color"]]
    
    savepath = f"../../Temp_Visualizations/GraphMLs/{search_string}_career.graphml"
    g.save(savepath, format="graphml")
    print(f"\nBuild Graph with {len(g.vs)} nodes and {len(g.es)} edges")


def places_and_fish(data):
    ''' Makes Graph with 3 types of Nodes: 1x Concept Fish, Nx Years, nx Places
    '''
    id_to_entity = {e.id:e for e in data.entities}
    fish_appellation = id_to_entity[59672]
    searchString_to_place = {}
    year_places = defaultdict(list)
    
    for concept_relation in fish_appellation.incoming:
        concept = concept_relation.source
        for obj_relation in concept.incoming:
            obj = obj_relation.source
            if obj.short_type in ("E19","E20"):
                for place_relation in obj.outgoing:
                    place = place_relation.target
                    if place.short_type == "E53":
                        if place.search_string in searchString_to_place:
                            year_places[obj.year].append(searchString_to_place[place.search_string])
                        else:
                            year_places[obj.year].append(place)
                            searchString_to_place[place.search_string] = place
    
    g = Graph(directed=True)

    year_to_idx = {year:i for i, year in enumerate(year_places, start=1)}
    place_to_idx = {place:i for i,place in enumerate(searchString_to_place.values(), start=max(year_to_idx.values())+1)}

    g.add_vertices(1+len(year_to_idx)+len(place_to_idx))

    # concept to years
    g.add_edges([(0, i) for i in year_to_idx.values()])
    # years to places
    g.add_edges([(place_to_idx[place], year_to_idx[year]) for year, places in year_places.items() for place in places])

    g.vs["Label"] = ["Fische"] + [f"Jahr {year}" for year in year_to_idx] + [place.string for place in place_to_idx]
    g.vs["Color"] = ["#06b67e"] + ["#fc3915" for year in year_to_idx] + [place.color for place in place_to_idx]
    g.vs["r"] = [int(color[1:3], 16) for color in g.vs["Color"]]
    g.vs["g"] = [int(color[3:5], 16) for color in g.vs["Color"]]
    g.vs["b"] = [int(color[5:7], 16) for color in g.vs["Color"]]
    g.vs["a"] = [1.0  for color in g.vs["Color"]]
    
    savepath = f"../../Temp_Visualizations/GraphMLs/Fish_and_Places.graphml"
    g.save(savepath, format="graphml")
    print(f"\nBuild Graph with {len(g.vs)} nodes and {len(g.es)} edges")



if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)

    for e in data.entities:
        if e.year == 1899 and ("pisces" in e.search_string or "fisch" in e.search_string):
            print(e.id, e)
            for r in e.incoming: print("    ", r, r.source.id)
            print('\n')
            for r in e.outgoing: print("    ", r, r.target.id)
    #places_and_fish(data)
    #collector_career_graph(data, "seewald")
    #place_person_graph(data, "sumatra")
    #collection_place_graph(data, "odonaten")
    collection_place_graph(data, "mollus")
    for e in data.entities:
        if e.short_type == "E39" and "" in e.search_string and e.year==1899:
            print(e, e.year, e.id)
        #if "Joining" in e.type :
            #print(e, e.year, e.id)
