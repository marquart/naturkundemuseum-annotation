import os
import pickle

from ParseUIMAXMI import SemanticEntity, SemanticProperty

def has_type_in_neighborhood(entity, neighbor_type, radius=3):
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
    for p in entity.outgoing:
        if p.target.type.startswith(neighbor_type): return True
    for p in entity.incoming:
        if p.source.type.startswith(neighbor_type): return True
    return False

def has_type(entity, etype):
    for p in entity.outgoing:
        if p.target.type.startswith("E55 ") and p.target.string == etype: return True
    return False

def load_pickle(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data

if __name__ == "__main__":
    pickle_file = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    data = load_pickle(pickle_file)
    
    places = []
    for doc in data:
        for entity in doc["Entities"].values():
            if entity.type.startswith("E53 ") and not has_type(entity, "Building") and (has_type_in_neighborhood(entity, "E8 ") or has_type_in_neighborhood(entity, "E96 ")):
                places.append((doc["Year"], doc["Institution"], entity))
    for i,pl in enumerate(places):
        print(f"| {i:<3} | {pl[0]:<4} | {pl[1]:<85} | {pl[2].string:<50} |")
