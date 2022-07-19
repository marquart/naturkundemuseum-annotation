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
    def __init__(self, e, acquisitionsWeights):
        assert e.short_type in ("E8","E96")
        
        self.entity    = e
        self.holding   = None
        self.locations = defaultdict(list) #general_name: e
        self.givers    = defaultdict(list) #general_name: e
        self.weight    = acquisitionsWeights[e.id]
        
        for p in e.outgoing:
            if p.short_type == "P22":
                self.holding = p.target
            elif p.short_type == "P23":
                self.givers[general_name(p.target).lower()].append(p.target)
            elif p.short_type == "P24":
                stack = deque((p.target,))
                while stack:
                    cursor = stack.popleft()
                    for pp in cursor.outgoing:
                        if pp.short_type == "P53":
                            self.locations[pp.target.search_string].append(pp.target)
                        elif pp.short_type == "P46":
                            stack.append(pp.target)

def buildActorTable(acqusisitions):
    names     = defaultdict(list)
    locations = defaultdict(dict) #general_person_name:year:[[location_id, weight],...]
    holdings  = defaultdict(dict) #general_person_name:year:[[holding_id, weight],...]
    
    for a in acqusisitions:
        if a.holding:
            year = a.entity.year
            for g,l in a.givers.items():
                names[g] += l

                # Locations
                if year not in locations[g]: locations[g][year] = []
                for loc in a.locations.values():
                    locations[g][year].append((str(loc[0].id), a.weight))

                # Holdings
                if year not in holdings[g]: holdings[g][year] = []
                holdings[g][year].append((str(a.holding.id), a.weight))
    result = {}
    for person_search_string, person_entities in names.items():
        person_result = [general_name(person_entities[0]),[],[]]

        for year in sorted(locations[person_search_string]):
            person_result[1].append([year, [tup for tup in sorted(locations[person_search_string][year], key=itemgetter(1))]])
        for year in sorted(holdings[person_search_string]):
            person_result[2].append([year, [tup for tup in sorted(holdings[person_search_string][year], key=itemgetter(1))]])
        result[person_search_string] = person_result
    return result
            

def verbose_name(group):
    return group[-1].string
    
def general_name(e):
    if e.short_type == "E21": return e.string.split(' ')[-1]
    return e.string

def save_table(table, savepath="../Website/public/"):
    with open(os.path.join(savepath, "actor_relations.json"), 'w', encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=None)
    print(f"Wrote {len(table)} Actors with relations to locations and holdings per year to {savepath}")

if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)
    acquisitionsWeights = calculateWeights(data.entities)
    
    acqusisitions = [Acquisition(e, acquisitionsWeights) for e in data.entities if validAcquisition(e)]
    giverTable = buildActorTable(acqusisitions)
    save_table(giverTable)
