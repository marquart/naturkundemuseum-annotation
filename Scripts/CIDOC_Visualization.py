import os
import json
from collections import Counter, defaultdict
from subprocess import run

from ParseUIMAXMI import SemanticEntity, SemanticProperty
from CollectionStats import SemanticData

from matplotlib.colors import to_hex
import seaborn as sns

from bs4 import BeautifulSoup

def recursive_add(id, tmp_childs, tmp_nodes, nodes):
    for child in tmp_childs[id]:
        tmp_nodes[child] = nodes[child]
        recursive_add(child, tmp_childs, tmp_nodes, nodes)
    

def make_split(nodes, edges, split):
    tmp_childs = defaultdict(list)
    for e in edges:
        parent, child = e[0],e[1]
        if parent == "E1": continue
        tmp_childs[parent].append(child)
    
    tmp_nodes, tmp_edges = {}, []
    for id in split:
        tmp_nodes[id] = nodes[id]
        recursive_add(id, tmp_childs, tmp_nodes, nodes)
    
    for e in edges:
        parent, child = e[0],e[1]
        if parent in tmp_nodes or child in tmp_nodes:
            tmp_edges.append(e)
    
    tmp_nodes["E1"] = "E1 CRM Entity"
    return tmp_nodes, tmp_edges
    
    

def generateDOT(nodes, edges, facecolors, txtcolors):
    template = """
digraph CIDOC {
    bgcolor="transparent";
    fontname="sans-serif";
    node [style="filled" shape=box fontname="sans-serif" penwidth=0];
    edge [penwidth=1];
    splines="ortho";
    ratio=0.4;
    
    {
    

    NODES
    
    }
    
    EDGES

}
    """
    with_nodes = template.replace("NODES", '\n'.join([f'        {id} [label="{label}" fillcolor="{facecolors[id] if id in facecolors else "lightgrey"}" fontcolor="{txtcolors[id] if id in txtcolors else "black"}"];' for id, label in nodes.items()]))
    with_arrows = with_nodes.replace("EDGES", '\n    '.join(f"{e[0]} -> {e[1]}" for e in edges))
    
    return with_arrows
    
def generateSVG(dot, output_path):    
    success = run(("dot", "-Tsvg", "-o", output_path), input=dot, encoding='UTF-8')
    success.check_returncode()
    
    print(f"Created '{output_path}'")

if __name__ == "__main__":
    # Count Entitity types
    PICKLE_FILE = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    data = SemanticData(PICKLE_FILE, load=True)
    
    used_classes = Counter(e.short_type for e in data.entities)
    

    #facecmap = sns.cubehelix_palette(start=.5, rot=-.5, as_cmap=True, n_colors=max(used_classes.values()))
    facecmap = sns.color_palette("dark:#69d_r", as_cmap=True, n_colors=max(used_classes.values()))
    facecolors = {cl:to_hex(facecmap(i)) for cl, i in used_classes.most_common()}
    
    
    txtcmap = sns.color_palette("light:floralwhite", as_cmap=True, n_colors=max(used_classes.values()))
    txtcolors = {cl:to_hex(txtcmap(i)) for cl, i in used_classes.most_common()}
    print(to_hex(facecmap(0)))
    
    # Build hierarchy
    Ontology_File = "../Data/INCEpTION/cidoc_crm_v7-1-1.xml" #source: https://cidoc-crm.org/html/cidoc_crm_v7.1.1.xml, doc: https://cidoc-crm.org/html/cidoc_crm_v7.1.1.htm

    with open(Ontology_File, 'r', encoding="utf-8-sig") as f:
        xml = BeautifulSoup(f, "xml")
    
    classes = xml.find('classes').findChildren('class')
    
    nodes = {} #id:fullName
    edges = [] #str: id -> id
    for cl in classes:
        id = cl['id']
        label = cl.fullName.string
        assert id not in nodes
        nodes[id] = label
        for parent in cl.findChildren('subClassOf'):
            edges.append((parent['id'], id))
    for i,split in enumerate((("E2","E92","E52","E54"), ("E53","E77","E59"))):
        temp_nodes, temp_edges = make_split(nodes, edges, split)
        dot = generateDOT(temp_nodes, temp_edges, facecolors, txtcolors)
        generateSVG(dot, f"../Documentation/Visualizations/CIDOC_Hierarchy{i}.svg")
    
    