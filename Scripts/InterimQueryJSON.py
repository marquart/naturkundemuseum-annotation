import os
import json
from itertools import chain


def lookup_through_property(prop_id, name, lookup):
    return lookup["Entities"][str(lookup["Properties"][str(prop_id)][name])]

def visited(entity):
    return "component" in entity

def DFS(entity, component_id, component_lst, lookup):
    entity["component"] = 0
    for prop_id in entity["outgoing"]:
        neighbor = lookup_through_property(prop_id, "target", lookup)
        if neighbor["type"].startswith("E55 ") or visited(neighbor): continue
        DFS(neighbor, component_id, component_lst, lookup)
    for prop_id in entity["incoming"]:
        neighbor = lookup_through_property(prop_id, "source", lookup)
        if neighbor["type"].startswith("E55 ") or visited(neighbor): continue
        DFS(neighbor, component_id, component_lst, lookup)
    entity["component"] = component_id
    component_lst.append(entity)
    
def find_components(data):
    components = {}
    
    c_id = 1
    c_lst = []
    for entity in data["Entities"].values():
        if entity["type"].startswith("E55 "): continue
        if not visited(entity):
            DFS(entity, c_id, c_lst, data)

            components[c_id] = sorted(c_lst, key=lambda e: len(e["outgoing"]), reverse=True)
            c_id += 1
            c_lst = []
    
    #assert len(chain.from_iterable(components)) == len(data["Entities"])
    processed = len(list(chain.from_iterable(components.values())))
    types = len([e for e in data["Entities"].values() if e["type"].startswith("E55 ")])
    assert processed+types == len(data["Entities"])
    print(f"\n{data['Year'], data['Institution']}: Found {len(components)} Components for {processed} Entities (from {len(data['Entities'])} Entities without {types} Types)")

    for c_id, c_lst in components.items():
        print(f"    Component {c_id}: {len(c_lst)} Entities, top: {c_lst[0]['type']} '{c_lst[0]['text']}' with {len(c_lst[0]['outgoing'])} targets")
    return components
    

def load_jsons(dirpath):
    result = []
    for file in os.listdir(dirpath):
        if file.endswith(".json"):
            with open(os.path.join(dirpath, file), 'r', encoding="utf-8") as f:
                result.append(json.load(f))
            print(f"Loaded '{file}'")
    return result
    

if __name__ == "__main__":
    JSON_PATH = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/JSON/"
    berichte = load_jsons(JSON_PATH)
    for bericht in berichte:
        components = find_components(bericht)

    
    