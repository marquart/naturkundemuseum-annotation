import os
from operator import attrgetter
from collections import deque
from itertools import chain
import re
import pickle
from subprocess import run

from ParseUIMAXMI import SemanticEntity, SemanticProperty


class Node(object):
    def __init__(self, entity=None, _id=0, label=""):
        if isinstance(entity, SemanticEntity):
            self.entity = entity
            self.id = entity.id
            self.label = f"{entity.type}<BR/>({entity.id})|{clean(entity.string)}"
            
        else:
            self.entity = None
            self.id = _id
            self.label = label
        
    def __str__(self):
        return f"N{self.id}".replace('-','_')
        
class Arrow(object):
    def __init__(self, property, source, target, _id=0, verbose_label=""):
        if isinstance(property, SemanticProperty) and isinstance(source, Node) and isinstance(target, Node):
        
            self.id = property.id
            self.source = source
            self.target = target
            label = re.search("(^P\d?\d?\d) (.*)", property.type)
            if not label: print(property.type)
            if label:
                self.label = label.group(1)
                self.verbose_label = label.group(2)
            else:
                self.label = "P0"
                self.verbose_label = "Unknown"
            self.index = int(self.label.strip("P "))
        else:
            self.id = _id
            self.source = source
            self.target = target
            self.label = "..."
            self.verbose_label = verbose_label
            self.index = 0
    
    def __str__(self):
        return f'{str(self.source)} -> {str(self.target)} [xlabel="{self.label}"];'


def BFS(node, maxdepth=3):
    queue = deque([node])
    depths = {node.entity: 0}
    too_many_neighbors = {} # entity:node
    processed_properties = set()
    real_nodes = {}
    virtual_nodes, arrows = [], []
    while queue:
        node = queue.popleft()
        assert isinstance(node, Node)
        if depths[node.entity] > maxdepth:
            break
        if (neighbors := len(node.entity.incoming)+len(node.entity.outgoing))>18-len(real_nodes) and depths[node.entity]>0:
            excuse = Node(_id=-1*node.id, label=f"...|{neighbors} Neighbors")
            arrows.append(Arrow(None, node, excuse, _id=-1*node.id, verbose_label="too many neighbors to draw"))
            virtual_nodes.append(excuse)
            too_many_neighbors[node.entity] = node
            continue
            
        for property in node.entity.outgoing:
            neighbour = property.target
            if neighbour in depths:
                if property in processed_properties:
                    continue
                elif neighbour in too_many_neighbors:
                    arrows.append(Arrow(property, node, too_many_neighbors[neighbour]))
                    processed_properties.add(property)
                else:
                    arrows.append(Arrow(property, node, real_nodes[neighbour]))
                    processed_properties.add(property)
                continue
            
            neighbour_node = Node(neighbour)
            real_nodes[neighbour] = neighbour_node
            arrows.append(Arrow(property, node, neighbour_node))
            processed_properties.add(property)
            queue.append(neighbour_node)
            depths[neighbour] = depths[node.entity] + 1
        for property in node.entity.incoming:
            neighbour = property.source
            if neighbour in depths:
                if property in processed_properties:
                    continue
                elif neighbour in too_many_neighbors:
                    arrows.append(Arrow(property, too_many_neighbors[neighbour], node))
                    processed_properties.add(property)
                else:
                    arrows.append(Arrow(property, real_nodes[neighbour], node))
                    processed_properties.add(property)
                continue
            
            neighbour_node = Node(neighbour)
            real_nodes[neighbour] = neighbour_node
            arrows.append(Arrow(property, neighbour_node, node))
            processed_properties.add(property)
            queue.append(neighbour_node)
            depths[neighbour] = depths[node.entity] + 1
    return list(real_nodes.values()) + virtual_nodes, arrows


def traverse(node, visited, processed_properties, depth=3):
    ''' Perform BFS recursively on the graph
    Returns [...nodes], [...arrows]
    '''
    assert isinstance(node, Node)
    if depth<0: return [],[]
    if node.id in visited and visited[node.id]>0: return [],[]
    visited[node.id] = depth
    if (neighbors := len(node.entity.incoming)+len(node.entity.outgoing))>8 and depth<3:
        excuse = Node(_id=-1*node.id, label=f"...|{neighbors} Neighbors")
        relation = Arrow(None, node, excuse, _id=-1*node.id, verbose_label="too many neighbors to draw")
        return [excuse], [relation]
    nodes = []
    arrows = []
    for property in node.entity.incoming:
        if property in processed_properties: continue
        if property.source.id in visited and visited[property.source.id]>0: continue
        source = Node(property.source)
        nodes.append(source)
        arrows.append(Arrow(property, source, node))
        processed_properties.add(property)
        result = traverse(source, visited, processed_properties, depth=depth-1)
        nodes += result[0]
        arrows += result[1]
    for property in node.entity.outgoing:
        if property in processed_properties: continue
        if property.target.id in visited and visited[property.target.id]>0: continue
        target = Node(property.target)
        nodes.append(target)
        arrows.append(Arrow(property, node, target))
        processed_properties.add(property)
        result = traverse(target, visited, processed_properties, depth=depth-1)
        nodes += result[0]
        arrows += result[1]
    return nodes, arrows


def clean(txt):
    return txt.replace('\r\n', ' ').replace('\n', ' ').replace('‑', '').replace('-', '')

def load_pickle(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data
    
def generate_DOT(entity):
    template = """
digraph Annotationen {
    bgcolor="transparent";
    rankdir="LR";
    ranksep="0.8 equally";
    fontname="sans-serif"; 
    node [shape=record fontname="sans-serif"];
    edge [fontname="sans-serif"];
    splines=ortho;
    
    {
    

    LEGEND

    subgraph cluster_net {
        label="GRAPHLABEL";
        fontname="sans-serif";
     
NODES

    }
    }
    
    ARROWS

}
    """.replace("GRAPHLABEL", f"Neighbourhood for Entity No. {entity.id} in {entity.institution} ({entity.year})")
    nodes = [Node(entity)]
    #result = traverse(nodes[0], {}, set(), depth=3)
    result = BFS(nodes[0], maxdepth=3)
    nodes += result[0]
    arrows = sorted(result[1], key=attrgetter("index"))
    with_nodes = template.replace("NODES", '\n'.join([f'        {str(node)} [label=<{node.label}> color="{"black" if i>0 else "red"}"];' for i, node in enumerate(nodes)]))
    with_arrows = with_nodes.replace("ARROWS", '\n    '.join([str(arrow) for arrow in arrows]))
    
    #legend = "|".join(sorted(set(f"{{'{a.label}'|{a.verbose_label}}}" for a in arrows)))
    legend = sorted({a.label:a for a in arrows}.values(), key=attrgetter("index"))
    legend = "".join(f'<TR><TD ALIGN="left">{a.label}</TD><TD ALIGN="left">{a.verbose_label}</TD></TR>' for a in legend)
    with_legend = with_arrows.replace("LEGEND", f'    legend1 [shape=none label=<<TABLE BORDER="0" CELLBORDER="1" CELLPADDING="4">{legend}</TABLE>>];')
    
    return with_legend
    
def generateSVG(pickle_path, output_path, entity_id=None):
    data = {e.id:e for e in chain.from_iterable([doc["Entities"].values() for doc in load_pickle(pickle_path)])}
    if not entity_id:
        last_item = max(data)
        #entity = data[-2]["Entities"][4732]#sehr kurz[4347]#[4732]#[4322]#[4325]#[4566]
        entity = data[last_item]
    else:
        entity = data[entity_id]
    svg_path = os.path.join(output_path, f"{entity.id}.svg")
    dot = generate_DOT(entity)
    
    success = run(("dot", "-Tsvg", "-o", svg_path), input=dot, encoding='UTF-8')
    success.check_returncode()
    
    print(f"Created '{svg_path}'")
    
    
if __name__ == "__main__":
    pickle_file = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    svg_filepath = "C:/Users/Aron/Documents/Naturkundemuseum/Visualizations/DOTs/"
    generateSVG(pickle_file, svg_filepath, entity_id=6922)
    #generateSVG(pickle_file, svg_filepath)
    '''
    pickle_file = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    data = load_pickle(pickle_file)
    
    dot_filepath = "C:/Users/Aron/Documents/Naturkundemuseum/Visualizations/DOTs/4325.gv"
    last_item = max(data[-1]["Entities"])
    entity = data[-2]["Entities"][4732]#sehr kurz[4347]#[4732]#[4322]#[4325]#[4566]
    #entity = data[-1]["Entities"][last_item]
    dot = generate_DOT(entity)
    print(dot)
    with open(dot_filepath, 'w', encoding="utf-8") as f:
        f.write(dot)
    # to generate SVG use: dot -Tsvg -o output.svg .\4325.gv
    '''
    