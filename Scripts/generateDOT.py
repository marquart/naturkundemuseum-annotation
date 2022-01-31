import os
from operator import attrgetter
import re
import pickle

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

def traverse(node, visited, processed_properties, depth=3):
    ''' Returns [...nodes], [...arrows]
    '''
    assert isinstance(node, Node)
    if depth<0: return [],[]
    if node.id in visited and visited[node.id]>0: return [],[]
    visited[node.id] = depth
    if (neighbors := len(node.entity.incoming)+len(node.entity.outgoing))>8 and depth<2:
        excuse = Node(_id=-1*node.id, label=f"...|{neighbors} Nachbarn")
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
    rankdir="LR";
    ranksep="0.8 equally";
    fontname="sans-serif"; 
    node [shape=record fontname="sans-serif"];
    edge [fontname="sans-serif"];
    splines=ortho;
    
    {
    

    LEGEND

    subgraph cluster_net {
        label="Graph";
        fontname="sans-serif";
     
NODES

    }
    }
    
    ARROWS

}
    """
    nodes = [Node(entity)]
    result = traverse(nodes[0], {}, set(), depth=3)
    nodes += result[0]
    arrows = sorted(result[1], key=attrgetter("index"))
    with_nodes = template.replace("NODES", '\n'.join([f'        {str(node)} [label=<{node.label}> color="{"black" if i>0 else "red"}"];' for i, node in enumerate(nodes)]))
    with_arrows = with_nodes.replace("ARROWS", '\n    '.join([str(arrow) for arrow in arrows]))
    
    #legend = "|".join(sorted(set(f"{{'{a.label}'|{a.verbose_label}}}" for a in arrows)))
    legend = sorted({a.label:a for a in arrows}.values(), key=attrgetter("index"))
    legend = "".join(f'<TR><TD ALIGN="left">{a.label}</TD><TD ALIGN="left">{a.verbose_label}</TD></TR>' for a in legend)
    with_legend = with_arrows.replace("LEGEND", f'    legend1 [shape=none label=<<TABLE BORDER="0" CELLBORDER="1" CELLPADDING="4">{legend}</TABLE>>];')
    
    return with_legend
    

if __name__ == "__main__":
    pickle_file = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    data = load_pickle(pickle_file)
    
    dot_filepath = "C:/Users/Aron/Documents/Naturkundemuseum/Visualizations/DOTs/4325.gv"
    entity = data[-1]["Entities"][4732]#sehr kurz[4347]#[4732]#[4322]#[4325]#[4566]
    dot = generate_DOT(entity)
    print(dot)
    with open(dot_filepath, 'w', encoding="utf-8") as f:
        f.write(dot)
    # to generate SVG use: dot -Tsvg -o output.svg .\4325.gv
    