import os
from operator import attrgetter
from collections import deque
import re
import pickle
import argparse
import html
from subprocess import run

from timeit import default_timer as timer

from SemanticModels import SemanticEntity, SemanticProperty, SemanticData

from BuildGraph import exportGraphMLfromTree

# for Temp Website
import random, json

class Node(object):
    def __init__(self, entity=None, _id=0, label="", style="filled", fontsize=11, virtual=False, renderYear=False):
        if isinstance(entity, SemanticEntity):
            self.entity = entity
            self.id = entity.id
            self.style = style
            self.fontsize = fontsize
            self.class_ = "entityNode"
            self.neighbor = virtual
            self.color = entity.color
            self.renderYear = renderYear
            
            if renderYear and entity.year>0:
                self.label = f"{entity.type}<BR/>({entity.id})<BR/>Year {entity.year}|{html.escape(entity.string)}"
            else:
                self.label = f"{entity.type}<BR/>({entity.id})|{html.escape(entity.string)}"
            
        else:
            self.entity = None
            self.id = _id
            self.label = label
            self.style = style
            self.fontsize = fontsize
            self.class_ = "entityNode"
            self.neighbor = virtual
            self.color = "#d3d3d3"
            self.renderYear = renderYear
        
    def __str__(self):
        if self.id < 0: return f"V{self.id}".replace('-','_')
        return f"N{self.id}"
    def __len__(self):
        if self.entity: return len(self.entity.incoming)+len(self.entity.outgoing)
        return float('inf')


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
    excuse = Node(_id=-1*entity.id, label=f"...|{neighbors} Neighbours", virtual=True)
    arrows.append(Arrow(None, node, excuse, _id=-1*node.id, verbose_label="too many neighbours to draw"))
    virtual_nodes.append(excuse)

def BFS_rule_cut(node, maxdepth=3, renderYear=False):
    ''' cuts edges for subtree based on entity type (E55 Type, E41 Appellation, E78 Curated Holding, E28 Conceptual Object, E53 Place)
    '''
    exclude = ("E55", "E41", "E78", "E28", "E53") # children will not get processed
    complete_exclude = ("E55", "E41", ) # Entities will get completely ignored 
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
        if node.entity.short_type in exclude and depths[node.entity]>0:
            neighbors = len(node)
            add_virtual_node(node, arrows, virtual_nodes, neighbors=neighbors)
            too_many_neighbors[node.entity] = node
            continue
            
        for property in node.entity.outgoing:
            neighbour = property.target
            if neighbour.short_type in complete_exclude: continue
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
            neighbour_node = Node(neighbour, renderYear=renderYear)
            real_nodes[neighbour] = neighbour_node
            arrows.append(Arrow(property, node, neighbour_node))
            processed_properties.add(property)
            queue.append(neighbour_node)
            depths[neighbour] = depths[node.entity] + 1
            if depths[neighbour]>maxdepth and len(neighbour.incoming)+len(neighbour.outgoing)>1:
                add_virtual_node(neighbour_node, arrows, virtual_nodes)
        for property in node.entity.incoming:
            neighbour = property.source
            if neighbour.short_type in complete_exclude: continue
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
            
            neighbour_node = Node(neighbour, renderYear=renderYear)
            real_nodes[neighbour] = neighbour_node
            arrows.append(Arrow(property, neighbour_node, node))
            processed_properties.add(property)
            queue.append(neighbour_node)
            depths[neighbour] = depths[node.entity] + 1
            if depths[neighbour]>maxdepth and len(neighbour.incoming)+len(neighbour.outgoing)>1:
                add_virtual_node(neighbour_node, arrows, virtual_nodes)
    return list(real_nodes.values()) + virtual_nodes, arrows


def BFS_quantity_cut(node, maxdepth=3, renderYear=False):
    ''' cuts edges for subtree based on threshold of nodes (18)
    '''
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
        if (neighbors := len(node))-len(real_nodes)>18 and depths[node.entity]>0:
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
            neighbour_node = Node(neighbour, renderYear=renderYear)
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
            
            neighbour_node = Node(neighbour, renderYear=renderYear)
            real_nodes[neighbour] = neighbour_node
            arrows.append(Arrow(property, neighbour_node, node))
            processed_properties.add(property)
            queue.append(neighbour_node)
            depths[neighbour] = depths[node.entity] + 1
            if depths[neighbour]>maxdepth and len(neighbour.incoming)+len(neighbour.outgoing)>1:
                add_virtual_node(neighbour_node, arrows, virtual_nodes)
    return list(real_nodes.values()) + virtual_nodes, arrows


def needsRenderYears(root_entity):
    """ Neighbors should display Years if the root is an E41 Appellation in Metadata
    """
    return root_entity.short_type == "E41" and root_entity.institution == "Metadata"
    

def count_nodes(nodes):
    return len([node for node in nodes if not node.neighbor])


def build_tree(entity, depth=3, BFS_function=BFS_quantity_cut):
    nodes = [Node(entity, style="rounded,filled", fontsize=11)]
    result = BFS_function(nodes[0], maxdepth=depth, renderYear=needsRenderYears(entity))
    nodes += result[0]
    arrows = sorted(result[1], key=attrgetter("index"))
    return count_nodes(nodes), nodes, arrows


def calculate_optimal_tree(entity, optimal_nodes=13, BFS_function=BFS_quantity_cut, exportGraphml=False):
    trees, no_nodes = {}, {} #depth:tree, depth:number of nodes
    for i in range(0,5):
        no, nodes, arrows = build_tree(entity, depth=i, BFS_function=BFS_function)
        if no == optimal_nodes:
            print(f"Optimal Tree for {str(entity)} with depth {i} ({no} nodes)")
            return generate_DOT(entity, depth=i, tree=(nodes,arrows)), i
        else:
            trees[i] = (nodes, arrows)
            no_nodes[i] = no
            
    optimal_depth = min(no_nodes, key=lambda x: abs(optimal_nodes-no_nodes[x]))
    nodes, arrows = trees[optimal_depth][0] , trees[optimal_depth][1]
    print(f"    Optimal Tree for {str(entity)} with depth {optimal_depth} ({no_nodes[optimal_depth]} nodes) Alternatives {str(no_nodes)}")
    return generate_DOT(entity, depth=optimal_depth, tree=(nodes,arrows), exportGraphml=exportGraphml), optimal_depth


def generate_DOT(entity, depth=3, tree=None, BFS_function=BFS_quantity_cut, exportGraphml=False):
    #    
    template = """
digraph Annotationen {
    labelloc="t";
    label="GRAPHLABEL";
    bgcolor="none";
    rankdir="LR";
    ranksep="0.8 equally";
    fontname="Roboto";
    fontsize="11";
    node [shape=record fontname="Roboto" fontsize="11" penwidth=1];
    edge [fontname="Roboto" fontsize="10" penwidth=1];
    splines=ortho;
    penwidth=8;

    {
    
    subgraph legend {
        LEGEND
    }
    subgraph neighborhood {
        pencolor="none";
        node [style="filled" color="white"]
     
NODES

    }
    }
    
    ARROWS

}
    """
    if entity.year > 0: template = template.replace("GRAPHLABEL", f"Neighbourhood for Entity No. {entity.id} in {entity.institution} ({entity.year}) with depth {depth+1}")
    else: template = template.replace("GRAPHLABEL", f"Neighbourhood for Entity No. {entity.id} in {entity.institution} with depth {depth+1}")
    
    if tree is None: _, nodes, arrows = build_tree(entity, depth=depth, BFS_function=BFS_function)
    else: nodes, arrows = tree[0], tree[1]
    
    with_nodes = template.replace("NODES", '\n'.join([f'        {str(node)} [id={str(node)} class="{node.class_}" label=<{node.label}> fillcolor="{node.color}" color="{"black" if i<1 else "white"}" fontsize="{node.fontsize}" style="{node.style}"];' for i, node in enumerate(nodes)])) #style="{node.style}"
    
    with_arrows = with_nodes.replace("ARROWS", '\n    '.join([str(arrow) for arrow in arrows]))
    
    #legend = "|".join(sorted(set(f"{{'{a.label}'|{a.verbose_label}}}" for a in arrows)))
    legend = sorted({a.label:a for a in arrows}.values(), key=attrgetter("index"))
    if legend:
        legend = "".join(f'<TR><TD ALIGN="left">{a.label}</TD><TD ALIGN="left">{a.verbose_label}</TD></TR>' for a in legend)
        with_legend = with_arrows.replace("LEGEND", f'    legend1 [shape=none label=<<TABLE BORDER="0" CELLBORDER="1" CELLPADDING="4">{legend}</TABLE>>];')
    else:
        # Not connected to any other Entity :(
        with_legend = with_arrows.replace("LEGEND", "")
    
    if exportGraphml: exportGraphMLfromTree(nodes, arrows)
    return with_legend


def generateSVG(data, output_path, entity_id=None, depth=3, quantity_based_BFS=False, exportGraphml=False):
    if not isinstance(data, SemanticData): data = SemanticData(data)
    entities = {e.id:e for e in data.entities}
    if not entity_id:
        last_item = max(entities)
        #entity = data[-2]["Entities"][4732]#sehr kurz[4347]#[4732]#[4322]#[4325]#[4566]
        entity = entities[last_item]
    else:
        entity = entities[entity_id]
        
    svg_path = os.path.join(output_path, f"{entity.id}.{OUTPUT_FORMAT}")

    if quantity_based_BFS: BFS_function = BFS_quantity_cut
    else: BFS_function = BFS_rule_cut
    
    if type(depth) is int: dot = generate_DOT(entity, depth=depth, BFS_function=BFS_function, exportGraphml=exportGraphml)
    else: dot, depth = calculate_optimal_tree(entity, BFS_function=BFS_function, exportGraphml=exportGraphml)
    
    success = run(("dot", f"-T{OUTPUT_FORMAT}", "-o", svg_path), input=dot, encoding='UTF-8')
    while success.returncode != 0 and depth > 0:
        print(f"    Error for {str(entity)} in depth {depth}, trying with smaller depth")
        depth -= 1
        success = run(("dot", f"-T{OUTPUT_FORMAT}", "-o", svg_path), input=generate_DOT(entity, depth=depth), encoding='UTF-8')
    
    print(f"Created '{svg_path}'")
    

OUTPUT_FORMAT = "svg"
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', '-a', default=False, action='store_true')
    parser.add_argument('--entity', '-e', type=int, default=-1)
    parser.add_argument('--depth', '-d', type=int, default=-1)
    parser.add_argument('--rulebased', '-r', default=False, action='store_true')
    parser.add_argument('--graphml', '-g', default=False, action='store_true')
    parser.add_argument('--format', '-f', type=str, default="svg")

    
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    svg_filepath = "../Website/public/Data/graphs" if os.path.exists("../Website/public/Data/graphs") else "../../Temp_Visualizations/DOTs/"
    
    data = SemanticData(pickle_file)
    args = parser.parse_args()

    if args.format:
        OUTPUT_FORMAT = args.format.strip().lower()
    
    if args.all:
        #temp_export = []
        start = timer()
        for i,e in enumerate(data.entities):
            generateSVG(data, svg_filepath, entity_id=e.id, depth=None)
            #if i > 30: break

        end = timer()
        #random.shuffle(temp_export)
        print(f"\nNeeded {(end-start)/60} Minutes")
        #with open("../Website/src/data/Temp_SVG_Lookup.json", 'w', encoding="UTF-8") as f:
            #json.dump(temp_export, f)
    else:
        if args.depth > -1: depth = args.depth
        else: depth = None
        
        if args.entity > -1: generateSVG(data, svg_filepath, entity_id=args.entity, depth=depth, exportGraphml=args.graphml)
        else: generateSVG(data, svg_filepath, entity_id=None, depth=depth, exportGraphml=args.graphml)
