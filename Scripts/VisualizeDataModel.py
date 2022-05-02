import os
from collections import deque, Counter
from subprocess import run

from ParseUIMAXMI import SemanticEntity, SemanticProperty, SemanticData

from matplotlib.colors import to_hex
import seaborn as sns


class Entity_Node(object):
    def __init__(self, entity_type):
        self.label = entity_type
        self.count = 1
        self.outgoing = Counter()
        self.incoming = Counter()
        
    def __str__(self):
        return self.label

class Property_Node(object):
    def __init__(self, property_type, source_node, target_node):
        self.label = property_type
        self.count = 1
        self.source = source_node
        self.target = target_node
        
    def __str__(self):
        return self.label


def add_entity_node(entity_nodes, entity):
    if entity.short_type in entity_nodes:
        entity_nodes[entity.type].count += 1
    else:
        entity_nodes[entity.type] = Entity_Node(entity.type)
    return entity_nodes, entity_nodes[entity.type]


def add_property_node(property_nodes, entity_nodes, property):
    id = (property.type, property.source.type, property.target.type)
    if id in property_nodes:
        property_nodes[id].count += 1
    else:
        entity_nodes, source_node = add_entity_node(entity_nodes, property.source)
        entity_nodes, target_node = add_entity_node(entity_nodes, property.target)
        property_nodes[id] = Property_Node(property.type, source_node, target_node)
    return property_nodes, entity_nodes


def BFS(entity, maxdepth=1):
    queue = deque([entity])
    depths = {entity: 0}

    processed_properties = set()
    entity_nodes = {}
    property_nodes = {}
    while queue:
        entity = queue.popleft()
        if depths[entity] > maxdepth:
            break
        for property in entity.outgoing:
            neighbour = property.target
            if neighbour in depths:
                if property in processed_properties:
                    continue
                else:
                    property_nodes, entity_nodes = add_property_node(property_nodes, entity_nodes, property) 
                    processed_properties.add(property)
                continue
            
            property_nodes, entity_nodes = add_property_node(property_nodes, entity_nodes, property)
            processed_properties.add(property)
            queue.append(neighbour)
            depths[neighbour] = depths[entity] + 1

        for property in entity.incoming:
            neighbour = property.source
            if neighbour in depths:
                if property in processed_properties:
                    continue
                else:
                    property_nodes, entity_nodes = add_property_node(property_nodes, entity_nodes, property) 
                    processed_properties.add(property)
                continue
            
            property_nodes, entity_nodes = add_property_node(property_nodes, entity_nodes, property)
            processed_properties.add(property)
            queue.append(neighbour)
            depths[neighbour] = depths[entity] + 1
    return entity_nodes, property_nodes


def bad_get_color(entity_type):
    if entity_type:
        LOOKUP = {'E41 ': '#debb9b', 'E63 ': '#50c4c2aa', 'E74 ': '#3b95c4aa', 'E21 ': '#3b95c4aa', 'E52 ': '#50c4c2aa', 'E55 ': '#06b67eaa', 'E85 ': '#fc3915aa', 'E28 ': '#06b67eaa', 'E19 ': '#5a50c4aa', 'E87 ': '#fc3915aa', 'E78 ': '#b560d4aa', 'E8 ': '#fc3915aa', 'E53 ': '#fc7715aa', 'E39 ': '#3b95c4aa', 'E54 ': '#50c4c2aa', 'E20 ': '#5a50c4aa', 'E35 ': '#debb9b', 'E77 ': '#b560d4aa', 'E9 ': '#fc3915aa', 'E12 ': '#fc3915aa', 'E60 ': '#debb9b', 'E7 ': '#fc3915aa', 'E96 ': '#fc3915aa', 'E86 ': '#fc3915aa', 'E57 ': '#5a50c4aa', 'E3 ': '#50c4c2aa', 'E66 ': '#fc3915aa', 'E29 ': '#debb9b', 'E73 ': '#debb9b', 'E11 ': '#fc3915aa', 'E14 ': '#fc3915aa', 'E79 ': '#fc3915aa'}
        for e in LOOKUP:
            if entity_type.startswith(e): return LOOKUP[e]
    return 'lightgrey'


def ffloat(no, count):
    return f"{round(no/count*100,1)}%"


def generate_DOT(entity_short_type, count, entity_nodes, properties):
    template = """
digraph Annotationen {
    bgcolor="transparent";
    rankdir="LR";

    fontname="Roboto";
    fontsize="11";
    node [shape=record fontname="Roboto" fontsize="11" penwidth=1];
    edge [fontname="sans-serif" fontsize="10" penwidth=1];
    splines="ortho";
    penwidth=8;
    
    {
    
    subgraph net {
        label="GRAPHLABEL";
        fontname="Roboto";
        fontsize="11";
        penwidth=1;
        pencolor="transparent";
        node [style="filled" color="white" class="semanticentity"]
     
NODES
PROPERTIES

    }
    }
    
    ARROWS

}
    """.replace("GRAPHLABEL", f"Empirical Data Model for Entities of Type {entity_short_type}")

    node_id_lookup = {t:f"N{i}" for i,t in enumerate(entity_nodes)}
    prop_id_lookup = {t:f"P{i}" for i,t in enumerate(properties)}
    

    
    with_nodes = template.replace("NODES", '\n'.join(f'        {node_id_lookup[t]} [label=<{t}> fillcolor="{bad_get_color(t)}" color="{"black" if i<1 else "white"}" shape="ellipse"];' for i, t in enumerate(entity_nodes)))
    
    cmap = sns.color_palette("Blues", n_colors=11)
    with_properties = with_nodes.replace("PROPERTIES", '\n'.join(f'        {prop_id_lookup[t]} [label=<{t[0]}|{ffloat(properties[t], count)}> fillcolor="{to_hex(cmap[int(properties[t]/count*10)])}" color="{"black" if i<1 else "white"}" fontcolor="{"black" if properties[t]/count<0.7 else "white"}"];' for i, t in enumerate(properties)))
    
    with_arrows = with_properties.replace("ARROWS", '\n    '.join(f"{node_id_lookup[p[1]]} -> {prop_id_lookup[p]}\n {prop_id_lookup[p]} -> {node_id_lookup[p[2]]}" for p in properties))
   
    return with_arrows
    

def build_subgraph(semantic_data, entity_short_type, savepath, filter_threshold=0.01):
    count = 0
    neighbor_entities = Counter()
    properties = Counter()
    
    for entity in semantic_data.entities:
        if entity.short_type == entity_short_type:
            neighbors, neighbor_properties = BFS(entity, maxdepth=1)
            for p in neighbor_properties: properties[p] += 1
            for e in neighbors: neighbor_entities[e] += 1
            count += 1
    
    filtered_properties = {p:c for p,c in properties.most_common() if c/count>filter_threshold}
    used_entity_type = set(pp for p in filtered_properties for pp in p[1:])
    
    dot = generate_DOT(entity_short_type, count, {e:c for e,c in neighbor_entities.items() if e in used_entity_type}, filtered_properties)
    
    success = run(("dot", "-Tsvg", "-o", savepath), input=dot, encoding='UTF-8')
    success.check_returncode()
    
    print(f"Created '{savepath}'")


if __name__ == "__main__":
    svg_path = "../../Temp_Visualizations/DataModel_E8.svg"
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)
    build_subgraph(data, "E8", svg_path, filter_threshold=0.05)
