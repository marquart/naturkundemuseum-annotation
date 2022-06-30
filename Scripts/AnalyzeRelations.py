import os
from operator import attrgetter
from collections import defaultdict, Counter
import re
import pickle
import argparse
import json

from matplotlib.colors import LinearSegmentedColormap, to_hex

from SemanticModels import SemanticEntity, SemanticProperty, SemanticData


def general_name(e):
    for p in e.outgoing:
        if p.target.short_type == "E41": # Appelation
            return p.target.string
    return e.string


def is_actor_in_acquisition(e):
    if e.short_type in ("E21","E74","E39"): #Person,Group,Actor
        for p in e.incoming:
            if p.short_type in ("P23","P22"): return True
    return False


def is_museums_collection(e):
    if e.short_type == "E78":
        for p in e.incoming:
            if p.short_type == "P22": return True
    return False


def identify_actors_for_collections(collection):
    collectors = []
    for p in collection.incoming:
        if p.short_type == "P22": #Donation, Purchase
            for pp in p.source.outgoing: # Acquisition
                if pp.short_type == "P23":
                    collectors.append(pp.target)
        elif p.short_type == "P23": #Trade
            for pp in p.source.outgoing: # Acquisition
                if pp.short_type == "P22":
                    collectors.append(pp.target)
    return collectors


def identify_locations_for_collections(collection):
    locations = []
    for p in collection.incoming:
        if p.short_type in ("P22","P23"):
            acquisitions_locations = []
            count = 0
            for pp in p.source.outgoing: # Acquisition
                if pp.short_type == "P24":
                    for ppp in pp.target.outgoing: # Object
                        if ppp.short_type == "P53":
                            acquisitions_locations.append(ppp.target)
                        elif ppp.short_type == "P46":
                            for pppp in ppp.target.outgoing: # Object
                                if pppp.short_type == "P53":
                                    acquisitions_locations.append(pppp.target)
                elif pp.short_type == "P23":
                    count += 1
            if count: locations += acquisitions_locations*count
            else: locations += acquisitions_locations
    return locations


def identify_locations_for_persons(actor):
    locations = []
    for p in actor.outgoing:
        if p.short_type == "P53":
            locations.append(p.target)
    for p in actor.incoming:
        if p.short_type == "P23":
            for pp in p.source.outgoing: # Acquisition
                if pp.short_type == "P24":
                    for ppp in pp.target.outgoing: # Object
                        if ppp.short_type == "P53":
                            locations.append(ppp.target)
                        elif ppp.short_type == "P46":
                            for pppp in ppp.target.outgoing: # Object
                                if pppp.short_type == "P53":
                                    locations.append(pppp.target)
    return locations
    

def build_actor_location_table(entities, table={}):
    '''Structure: {Person:{..year:{...place:count}}}
    '''
    #TYPE_PATTERN = re.compile(r"^Synonym for E21|E74|E39 ") #("E21","E74","E39"): # Person or Group or Actor
    actors = defaultdict(list) # Appelation: [...persons] or person: [person]
    for e in entities:
        if is_actor_in_acquisition(e):
            actors[general_name(e)].append(e)

    print(f"Found {len(actors)} generalized actors with {sum(len(l) for l in actors.values())} entities")
    for app, persons in actors.items():
        result = defaultdict(list) # year:locations
        for person in persons:
            locations = identify_locations_for_persons(person)
            if locations:
                result[person.year] += locations
        if result:
            assert app not in table
            table[app] = result
    
    print(f"Found locations for {len(table)} actors")
    return table


def build_holding_location_table(entities, table={}):
    '''Structure: {Person:{..year:{...place:count}}}
    '''
    #TYPE_PATTERN = re.compile(r"^Synonym for E[21|74|39]") #("E21","E74","E39"): # Person or Group or Actor
    holdings = defaultdict(list) # holding_string: [...persons] or person: [person]
    for e in entities:
        if is_museums_collection(e):
            holdings[general_name(e)].append(e)
        
    print(f"Found {len(holdings)} generalized holdings with {sum(len(l) for l in holdings.values())} entities")
    
    #collissions = []
    for app, collections in holdings.items():
        result = defaultdict(list) # year:locations
        for collection in collections:
            locations = identify_locations_for_collections(collection)
            if locations:
                result[collection.year] += locations
        if result:
            assert app not in table #if app in table: collissions.append(app)
            table[app] = result
    
    print(f"Found locations for {len(table)} holdings")
    #print([(str(x), x.id) for x in collissions])
    return table


def build_holding_actors_table(entities, table={}):
    holding_actors = defaultdict(dict) # collection_string: {..years: [..person_objs]}
    for e in entities:
        if is_museums_collection(e):
            collectors = identify_actors_for_collections(e)
            name = general_name(e)
            if e.year in holding_actors[name]:
                holding_actors[name][e.year] += collectors
            else:
                holding_actors[name][e.year] = collectors
    return holding_actors


def save_table(table, savepath="../Website/public/"):
    json_table = defaultdict(dict)
    for app, rows in table.items():
        reduced_row = []
        for year in sorted(rows):
            locations = Counter(rows[year])
            
            ranks = sorted(set(locations.values()))
            cmap = LinearSegmentedColormap.from_list(f"cmap{year}", ("#c7df7f", "#7da30b"), N=len(ranks))
            colors = {no:to_hex(cmap(i)) for i,no in enumerate(ranks, start=0)}
            
            reduced_row.append((year, [(str(place.id), count, colors[count]) for place, count in locations.most_common()]))
            
        json_table[app.id] = reduced_row
    with open(os.path.join(savepath, "location_relations.json"), 'w', encoding="utf-8") as f:
        json.dump(json_table, f, ensure_ascii=False, indent=None)
    print(f"Wrote {len(json_table)} Actors with relations to locations per year to {savepath}")


if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)
    person_locations_table = build_actor_location_table(data.entities) #person_string: {..years: ..[..location_objs]}
    collection_locations_table = build_holding_location_table(data.entities) #collection_string: {..years: ..[..location_objs]}
    person_collection_table = build_holding_actors_table(data.entities)
    
     
    save_table(table)
    
    #
