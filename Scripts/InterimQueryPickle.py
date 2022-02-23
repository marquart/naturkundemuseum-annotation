import os
import pickle

from ParseUIMAXMI import SemanticEntity, SemanticProperty

def print_neighborhood(entity, radius=3):
    if radius<1: return
    for p in entity.incoming:
        if not p.processed:
            print(str(p))
            p.processed = True
        print_neighborhood(p.source, radius=radius-1)
    for p in entity.outgoing:
        if not p.processed:
            print(str(p))
            p.processed = True
        print_neighborhood(p.target, radius=radius-1)


def has_type_in_neighborhood(entity, neighbor_type, radius=3):
    '''Returns True if the Entity is related with an Entity of type `neighbor_type` within an neighborhood (default radius of 3)'''
    if entity.type.startswith(neighbor_type): return True
    if radius<1: return False
    for p in entity.outgoing:
        result = has_type_in_neighborhood(p.target, neighbor_type, radius=radius-1)
        if result: return True
    for p in entity.incoming:
        result = has_type_in_neighborhood(p.source, neighbor_type, radius=radius-1)
        if result: return True
    return False
    

def has_neighbor_with_type(entity, neighbor_type):
    return has_type_in_neighborhood(entity, neighbor_type, radius=1)

def has_annotation_type(entity, content):
    '''Returns True if the Entity has a real Semantic Type (E55) with `content` as value'''
    for p in entity.outgoing:
        if p.target.type.startswith("E55 ") and p.target.string == content: return True
    return False

def rm_newline(text):
    text = text.replace('\r\n', ' ')
    return text.replace('\n', ' ')

def load_pickle(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data

if __name__ == "__main__":
    pickle_file = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    data = load_pickle(pickle_file)
    
    places = []
    other_places = []
    for doc in data:
        for entity in doc["Entities"].values():
            if entity.type.startswith("E53 ") and not has_annotation_type(entity, "Building"):
                if has_type_in_neighborhood(entity, "E8 ") or has_type_in_neighborhood(entity, "E96 "):
                    places.append((doc["Year"], doc["Institution"], entity))
                else:
                    other_places.append((doc["Year"], doc["Institution"], entity))
                
    conceptuals = 0
    for i,pl in enumerate(places):
            
        print(f"| {i:<3} | {pl[0]:<4} | {pl[1]:<85} | {pl[2].id:<4} | {rm_newline(pl[2].string):<50} |")
        if has_type_in_neighborhood(pl[2], "E28 ", radius=3): conceptuals += 1
    
    print('\n\n')
    for i,pl in enumerate(other_places):
        print(f"| {i:<3} | {pl[0]:<4} | {pl[1]:<85} | {pl[2].id:<4} | {rm_newline(pl[2].string):<50} |")
        #if pl[2].string == 'Peru':
            #print_neighborhood(pl[2])
    print(f"\n{conceptuals}")
