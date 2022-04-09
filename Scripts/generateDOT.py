import os
from operator import attrgetter
from collections import deque
from itertools import chain
import re
import pickle
import argparse
from subprocess import run

from timeit import default_timer as timer

from ParseUIMAXMI import SemanticEntity, SemanticProperty, SemanticData


class Node(object):
    def __init__(self, entity=None, _id=0, label="", style="bold"):
        if isinstance(entity, SemanticEntity):
            self.entity = entity
            self.id = entity.id
            self.label = f"{entity.type}<BR/>({entity.id})|{entity.string}"
            self.style = style
            
        else:
            self.entity = None
            self.id = _id
            self.label = label
            self.style = style
        
    def __str__(self):
        return f"N{self.id}".replace('-','_')
        
class Arrow(object):
    def __init__(self, property, source, target, _id=0, verbose_label=""):
        if isinstance(property, SemanticProperty) and isinstance(source, Node) and isinstance(target, Node):
        
            self.id = property.id
            self.source = source
            self.target = target

            self.label = property.short_type
            self.verbose_label = property.type.lstrip(self.label)

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

def add_virtual_node(node, arrows, virtual_nodes, neighbors=None):
    entity = node.entity
    if neighbors is None: neighbors = len(entity.incoming)+len(entity.outgoing)
    excuse = Node(_id=-1*entity.id, label=f"...|{neighbors} Neighbours", style="dashed")
    arrows.append(Arrow(None, node, excuse, _id=-1*node.id, verbose_label="too many neighbours to draw"))
    virtual_nodes.append(excuse)

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
            add_virtual_node(node, arrows, virtual_nodes, neighbors=neighbors)
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
            if depths[neighbour]>maxdepth and len(neighbour.incoming)+len(neighbour.outgoing)>1:
                add_virtual_node(neighbour_node, arrows, virtual_nodes)
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
            if depths[neighbour]>maxdepth and len(neighbour.incoming)+len(neighbour.outgoing)>1:
                add_virtual_node(neighbour_node, arrows, virtual_nodes)
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
        excuse = Node(_id=-1*node.id, label=f"...|{neighbors} Neighbours")
        relation = Arrow(None, node, excuse, _id=-1*node.id, verbose_label="too many neighbours to draw")
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


def get_color(node):
    if node.entity:
        LOOKUP = {'E41': '#debb9b', 'E63': '#50c4c2aa', 'E74': '#3b95c4aa', 'E21': '#3b95c4aa', 'E52': '#50c4c2aa', 'E55': '#06b67eaa', 'E85': '#fc3915aa', 'E28': '#06b67eaa', 'E19': '#5a50c4aa', 'E87': '#fc3915aa', 'E78': '#b560d4aa', 'E8': '#fc3915aa', 'E53': '#fc7715aa', 'E39': '#3b95c4aa', 'E54': '#50c4c2aa', 'E20': '#5a50c4aa', 'E35': '#debb9b', 'E77': '#b560d4aa', 'E9': '#fc3915aa', 'E12': '#fc3915aa', 'E60': '#debb9b', 'E7': '#fc3915aa', 'E96': '#fc3915aa', 'E86': '#fc3915aa', 'E57': '#5a50c4aa', 'E3': '#50c4c2aa', 'E66': '#fc3915aa', 'E29': '#debb9b', 'E73': '#debb9b', 'E11': '#fc3915aa', 'E14': '#fc3915aa', 'E79': '#fc3915aa'} #{'E41': '#debb9b', 'E21': '#a1c9f4', 'E52': '#fab0e4', 'E55': '#d0bbff', 'E74': '#a1c9f4', 'E63': '#fab0e4', 'E85': '#ff9f9b', 'E19': '#ffb482', 'E28': '#d0bbff', 'E8': '#ff9f9b', 'E39': '#a1c9f4', 'E78': '#b9f2f0', 'E87': '#ff9f9b', 'E53': '#8de5a1', 'E54': '#fab0e4', 'E20': '#ffb482', 'E35': '#debb9b', 'E9': '#ff9f9b', 'E77': '#b9f2f0', 'E12': '#ff9f9b', 'E60': '#debb9b', 'E7': '#ff9f9b', 'E3': '#fab0e4', 'E57': '#ffb482', 'E86': '#ff9f9b', 'E96': '#ff9f9b', 'E66': '#ff9f9b', 'E29': '#debb9b', 'E73': '#debb9b', 'E11': '#ff9f9b', 'E14': '#ff9f9b', 'E79': '#ff9f9b'}#{'E41': '#8c613c', 'E55': '#956cb4', 'E74': '#4878d0', 'E63': '#dc7ec0', 'E21': '#4878d0', 'E52': '#dc7ec0', 'E85': '#d65f5f', 'E8': '#d65f5f', 'E78': '#797979', 'E87': '#d65f5f', 'E28': '#956cb4', 'E53': '#6acc64', 'E20': '#ee854a', 'E54': '#dc7ec0', 'E19': '#ee854a', 'E39': '#4878d0', 'E35': '#8c613c', 'E12': '#d65f5f', 'E77': '#797979', 'E9': '#d65f5f', 'E60': '#8c613c', 'E7': '#d65f5f', 'E96': '#d65f5f', 'E86': '#d65f5f', 'E57': '#ee854a', 'E3': '#dc7ec0', 'E66': '#d65f5f', 'E29': '#8c613c', 'E11': '#d65f5f', 'E73': '#8c613c', 'E79': '#d65f5f', 'E14': '#d65f5f'}
        if node.entity.short_type in LOOKUP: return LOOKUP[node.entity.short_type]
    return 'lightgrey'


def count_nodes(nodes):
    return len([node for node in nodes if node.style != 'dashed'])


def build_tree(entity, depth=3):
    nodes = [Node(entity, style="bold")]
    result = BFS(nodes[0], maxdepth=depth)
    nodes += result[0]
    arrows = sorted(result[1], key=attrgetter("index"))
    return count_nodes(nodes), nodes, arrows


def calculate_optimal_tree(entity, optimal_nodes=13):
    trees, no_nodes = {}, {} #depth:tree, depth:number of nodes
    for i in range(0,5):
        no, nodes, arrows = build_tree(entity, depth=i)
        if no == optimal_nodes:
            print(f"Optimal Tree for {str(entity)} with depth {i} ({no} nodes)")
            return generate_DOT(entity, depth=i, tree=(nodes,arrows))
        else:
            trees[i] = (nodes, arrows)
            no_nodes[i] = no
            
    optimal_depth = min(no_nodes, key=lambda x: abs(optimal_nodes-no_nodes[x]))
    nodes, arrows = trees[optimal_depth][0] , trees[optimal_depth][1]
    print(f"    Optimal Tree for {str(entity)} with depth {optimal_depth} ({no_nodes[optimal_depth]} nodes) Alternatives {str(no_nodes)}")
    return generate_DOT(entity, depth=optimal_depth, tree=(nodes,arrows))


def generate_DOT(entity, depth=3, tree=None):
    template = """
digraph Annotationen {
    bgcolor="transparent";
    rankdir="LR";
    ranksep="0.8 equally";
    fontname="sans-serif";
    fontsize="11";
    node [shape=record fontname="sans-serif" fontsize="11" penwidth=1];
    edge [fontname="sans-serif" fontsize="10" penwidth=1];
    splines=ortho;
    penwidth=8;
    
    {
    
    subgraph legend {
        LEGEND
    }
    subgraph cluster_net {
        label="GRAPHLABEL";
        fontname="sans-serif";
        fontsize="11";
        penwidth=1;
        pencolor="transparent";
        node [style="filled" color="white" class="entities"]
     
NODES

    }
    }
    
    ARROWS

}
    """.replace("GRAPHLABEL", f"Neighbourhood for Entity No. {entity.id} in {entity.institution} ({entity.year}) with depth {depth+1}")
    
    if tree is None: _, nodes, arrows = build_tree(entity, depth=depth)
    else: nodes, arrows = tree[0], tree[1]
    
    with_nodes = template.replace("NODES", '\n'.join([f'        {str(node)} [label=<{node.label}> fillcolor="{get_color(node)}" color="{"black" if i<1 else "white"}"];' for i, node in enumerate(nodes)])) #style="{node.style}"
    with_arrows = with_nodes.replace("ARROWS", '\n    '.join([str(arrow) for arrow in arrows]))
    
    #legend = "|".join(sorted(set(f"{{'{a.label}'|{a.verbose_label}}}" for a in arrows)))
    legend = sorted({a.label:a for a in arrows}.values(), key=attrgetter("index"))
    legend = "".join(f'<TR><TD ALIGN="left">{a.label}</TD><TD ALIGN="left">{a.verbose_label}</TD></TR>' for a in legend)
    with_legend = with_arrows.replace("LEGEND", f'    legend1 [shape=none label=<<TABLE BORDER="0" CELLBORDER="1" CELLPADDING="4">{legend}</TABLE>>];')
    
    return with_legend
    
def generateSVG(data, output_path, entity_id=None, depth=3):
    if not isinstance(data, SemanticData): data = SemanticData(data)
    entities = {e.id:e for e in data.entities}
    if not entity_id:
        last_item = max(entities)
        #entity = data[-2]["Entities"][4732]#sehr kurz[4347]#[4732]#[4322]#[4325]#[4566]
        entity = entities[last_item]
    else:
        entity = entities[entity_id]
        
    svg_path = os.path.join(output_path, f"{entity.id}.svg")
    
    if type(depth) is int: dot = generate_DOT(entity, depth=depth)
    else: dot = calculate_optimal_tree(entity)
    
    success = run(("dot", "-Tsvg", "-o", svg_path), input=dot, encoding='UTF-8')
    success.check_returncode()
    
    print(f"Created '{svg_path}'")
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--entity', '-e', type=int, default=-1)
    parser.add_argument('--depth', '-d', type=int, default=-1)
    
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    svg_filepath = "../../Temp_Visualizations/DOTs/TestRun"
    
    data = SemanticData(pickle_file)

    args = parser.parse_args()
    start = timer()
    for i,e in enumerate(data.entities):
        generateSVG(data, svg_filepath, entity_id=e.id, depth=None)
        if i>99: break
    end = timer()
    print(f"\nNeeded {(end-start)/60} Minutes")
    '''
    if args.depth > -1: depth = args.depth
    else: depth = None
    
    if args.entity > -1: generateSVG(data, svg_filepath, entity_id=args.entity, depth=depth)
    else: generateSVG(data, svg_filepath, entity_id=None, depth=depth)
    '''