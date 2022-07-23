import os
from operator import attrgetter, itemgetter
from collections import defaultdict, Counter, deque
import re
import pickle
import json

from itertools import chain

from matplotlib.colors import LinearSegmentedColormap, to_hex

from SemanticModels import SemanticEntity, SemanticProperty, SemanticData
from ImportantAcquisition import calculateWeights, validAcquisition

class Acquisition(object):
    cmap = LinearSegmentedColormap.from_list("cmap", ("#c7df7f", "#7da30b"), N=10)
    
    def __init__(self, e, acquisitionsWeights):
        assert e.short_type in ("E8","E96")
        
        self.entity    = e
        self.holding   = None
        self.locations = []
        self.givers    = []
        self.weight    = acquisitionsWeights[e.id]
        self.color     = to_hex(Acquisition.cmap(self.weight))
        
        for p in e.outgoing:
            if p.short_type == "P22":
                self.holding = p.target
            elif p.short_type == "P23":
                self.givers.append(p.target)
            elif p.short_type == "P24":
                stack = deque((p.target,))
                while stack:
                    cursor = stack.popleft()
                    for pp in cursor.outgoing:
                        if pp.short_type == "P53":
                            self.locations.append(pp.target)
                        elif pp.short_type == "P46":
                            stack.append(pp.target)


def buildResult(column1, column2):
    result = {}
    for display_name in column1:
        entity_result = [[],[]]

        column1_data = column1[display_name]
        if display_name in column2: column2_data = column2[display_name]
        else: column2_data = {}

        #begin = min((min(column1_data.keys()), min(column2_data.keys())))
        #end = max((max(column1_data.keys()), max(column2_data.keys())))

        for i in range(1889, 1916):
            if i in column1_data: entity_result[0].append(column1_data[i])
            else: entity_result[0].append([])

            if i in column2_data: entity_result[1].append(column2_data[i])
            else: entity_result[1].append([])

        result[display_name] = entity_result
    return result


def buildActorTable(acqusisitions):
    generalized_names = {} # {general_name: [general_name_verbose, [...alternative names]]}
    column1           = defaultdict(dict) #if locations this is locations else persons #general_name_verbose:year:[[location_id, weight],...]
    column2           = defaultdict(dict) #general_person_name:year:[[holding_id, weight],...]
    
    for a in acqusisitions:
        if a.holding:
            year = a.entity.year
            for person in a.givers:
                # Generalization of names
                search_name = general_name(person)
                display_name = general_name_verbose(person)
                if search_name in generalized_names: generalized_names[search_name][1].add(person.string)
                else: generalized_names[search_name] = (display_name, set((person.string,)))

                # Locations
                if year not in column1[display_name]: column1[display_name][year] = []
                for loc in a.locations:
                    column1[display_name][year].append((str(loc.id), a.weight+11, a.color))

                # Holdings
                if year not in column2[display_name]: column2[display_name][year] = []
                column2[display_name][year].append((str(a.holding.id), a.weight+11, a.color))

    result = buildResult(column1, column2)
    return makeJSONready(generalized_names), result


def buildCollectionTable(acqusisitions):
    generalized_names = {} # {general_name: [general_name_verbose, [...alternative names]]}
    column1           = defaultdict(dict) #if locations this is locations else persons #general_name_verbose:year:[[location_id, weight],...]
    column2           = defaultdict(dict) #general_person_name:year:[[holding_id, weight],...]
    
    for a in acqusisitions:
        if a.holding:
            year = a.entity.year
            collection = a.holding
            
            # Generalization of names
            search_name = general_name(collection)
            display_name = general_name_verbose(collection)
            if search_name in generalized_names: generalized_names[search_name][1].add(collection.string)
            else: generalized_names[search_name] = (display_name, set((collection.string,)))

            # Locations
            if year not in column1[display_name]: column1[display_name][year] = []
            for loc in a.locations:
                column1[display_name][year].append((str(loc.id), a.weight+11, a.color))

            # actors
            if year not in column2[display_name]: column2[display_name][year] = []
            for person in a.givers:
                column2[display_name][year].append((str(person.id), a.weight+11, a.color))

    result = buildResult(column1, column2)
    return makeJSONready(generalized_names), result


def buildLocationTable(acqusisitions):
    generalized_names = {} # {general_name: [general_name_verbose, [...alternative names]]}
    column1           = defaultdict(dict) #if locations this is locations else persons #general_name_verbose:year:[[location_id, weight],...]
    column2           = defaultdict(dict) #general_person_name:year:[[holding_id, weight],...]
    
    for a in acqusisitions:
        if a.holding:
            year = a.entity.year
            for location in a.locations:
                # Generalization of names
                search_name = general_name(location)
                display_name = general_name_verbose(location)
                if search_name in generalized_names: generalized_names[search_name][1].add(location.string)
                else: generalized_names[search_name] = (display_name, set((location.string,)))

                # Persons
                if year not in column1[display_name]: column1[display_name][year] = []
                for person in a.givers:
                    column1[display_name][year].append((str(person.id), a.weight+11, a.color))

                # Holdings
                if year not in column2[display_name]: column2[display_name][year] = []
                column2[display_name][year].append((str(a.holding.id), a.weight+11, a.color))

    result = buildResult(column1, column2)
    return makeJSONready(generalized_names), result

def makeJSONready(d):
    reslt = []
    for k,v in d.items():
        reslt.append([k, v[0], list(v[1])]) #search_string, display string, list of alternative forms
    return reslt

def general_name(e):
    if e.short_type == "E21": return e.string.split(' ')[-1].lower()
    return e.search_string

def general_name_verbose(e):
    if e.short_type == "E21": return e.string.split(' ')[-1]
    return e.string

def save_tables(tables, filepath):
    assert len(tables) == 2
    with open(filepath, 'w', encoding="utf-8") as f:
        json.dump(list(tables), f, ensure_ascii=False, indent=None)

    print(f"Wrote {len(tables[0])} entities with relations per year to {filepath}")

if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)
    acquisitionsWeights = calculateWeights(data.entities)
    
    acqusisitions = [Acquisition(e, acquisitionsWeights) for e in data.entities if validAcquisition(e)]
    giverNames, giverAcquisitions           = buildActorTable(acqusisitions)
    collectionNames, collectionAcquisitions = buildCollectionTable(acqusisitions)
    locationNames, locationAcquisitions     = buildLocationTable(acqusisitions)
    
    save_tables((giverNames, giverAcquisitions), filepath="../Website/public/Persons.json")
    save_tables((collectionNames, collectionAcquisitions), filepath="../Website/public/Collections.json")
    save_tables((locationNames, locationAcquisitions), filepath="../Website/public/Locations.json")
