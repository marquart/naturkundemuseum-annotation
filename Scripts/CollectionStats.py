import pickle
import os
from itertools import chain
from collections import defaultdict, Counter
from ParseUIMAXMI import SemanticEntity, SemanticProperty, stats_directory

import matplotlib.pyplot as plt
import seaborn as sns

class SemanticData(object):
    def __init__(self, filepath, load=True):
        if load: self.data = self.load_pickle(filepath)
        else: self.data = stats_directory(filepath, save=False, consolidate=False)
        
        self.entities = list(chain.from_iterable(file["Entities"].values() for file in self.data))
        self.properties = list(chain.from_iterable(file["Properties"].values() for file in self.data))
        
    def load_pickle(self, filepath):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        return data


def has_mammaliakeyword(entity):
    search_str = entity.string.replace(' ','').lower()
    return "äuge" in search_str or "ammal" in search_str or "irbelt" in search_str
    

def is_museumcollection(entity):
    if entity.type.startswith("E78"):
        for prop in entity.incoming:
            if prop.type.startswith("P22"): return True
    return False


def is_part_of_acquisition(entity):
    for p in entity.incoming:
        if p.type.startswith("P24"): return entity
        if p.type.startswith("P130") or p.type.startswith("P128"):
            for pp in p.source.incoming:
                if pp.type.startswith("P24"): return p.source
    return None


def is_mammalia_acquisition_object(entity):
    if entity.institution.startswith("Zoo") and has_mammaliakeyword(entity):
        return is_part_of_acquisition(entity)
    return None

def is_mammaliacollection(entity):
    if entity.institution.startswith("Zoo") and is_museumcollection(entity):
        return has_mammaliakeyword(entity)
    return False


def find_mammalia_entities(data):
    mammalias = set()
    for entity in data.entities:
        if is_mammaliacollection(entity):
            mammalias.add(entity)
        elif (corr_obj := is_mammalia_acquisition_object(entity)):
            mammalias.add(corr_obj)
    return mammalias

def parse_dimension(e):
    try:
        return int(e.string.replace(' ',''))
    except ValueError:
        return 0

def has_relation(entity, propclass, eclass, estring):
    for p in entity.outgoing:
        if p.type.startswith(propclass) and p.target.type.startswith(eclass) and estring in p.target.string: return True
    for p in entity.incoming:
        if p.type.startswith(propclass) and p.source.type.startswith(eclass) and estring in p.source.string: return True
    return False

def get_object_counts(entities):
    ''' e should be E78 or E19/E20
    '''
    count = 0
    for e in entities:
        if e.type.startswith("E78"):
            for p in e.incoming:
                if p.type.startswith("P22"):
                    acquisition = p.source
                    for pp in acquisition.outgoing:
                        if pp.type.startswith("P43"):
                            count += parse_dimension(pp.target)
                        elif pp.type.startswith("P24"):
                            if pp.target in entities: continue
                            for ppp in pp.target.outgoing:
                                if ppp.type.startswith("P43"):
                                    if has_relation(ppp.target, "P2", "E55", "chlussnu"): continue
                                    count += parse_dimension(ppp.target)
        elif e.type.startswith("E19") or e.type.startswith("E20"):
            for p in e.outgoing:
                if p.type.startswith("P43"):
                    if has_relation(p.target, "P2", "E55", "chlussnu"): continue
                    count += parse_dimension(p.target)
        else:
            print("Unexpected type found: ", e.verbose())
    return count

def acquisitions_to_holding(e):
    assert e.type.startswith("E78")
    for p in e.incoming:
        if p.type.startswith("P22"):
            yield p.source


def acquisitions_to_obj(e):
    assert e.type.startswith("E19") or e.type.startswith("E20")
    for p in e.incoming:
        if p.type.startswith("P24"):
            yield p.source

def get_object_counts(entities):
    ''' e should be E78 or E19/E20
    '''
    count = 0
    for e in entities:
        if e.type.startswith("E78"):
            for acquisition in acquisitions_to_holding(e):
                for pp in acquisition.outgoing:
                    if pp.type.startswith("P43"):
                        count += parse_dimension(pp.target)
                    elif pp.type.startswith("P24"):
                        if pp.target in entities: continue
                        for ppp in pp.target.outgoing:
                            if ppp.type.startswith("P43"):
                                if has_relation(ppp.target, "P2", "E55", "chlussnu"): continue
                                count += parse_dimension(ppp.target)
        elif e.type.startswith("E19") or e.type.startswith("E20"):
            for p in e.outgoing:
                if p.type.startswith("P43"):
                    if has_relation(p.target, "P2", "E55", "chlussnu"): continue
                    count += parse_dimension(p.target)
        else:
            print("Unexpected type found: ", e.verbose())
    return count

def count_acquisitions(entities):
    '''returns approximate number of (acquisitions, donors, objects)
    '''
    acquisitions, donors, objects = 0, 0, get_object_counts(entities)
    for e in entities:
        enitity_donors = 0
        if e.type.startswith("E78"):
            for acquisition in acquisitions_to_holding(e):
                for p in acquisition.outgoing:
                    if p.type.startswith("P23"): enitity_donors += 1
        elif e.type.startswith("E19") or e.type.startswith("E20"):
            for acquisition in acquisitions_to_obj(e):
                for p in acquisition.outgoing:
                    if p.type.startswith("P23"): enitity_donors += 1
        else:
            assert False
        donors += enitity_donors
        if enitity_donors>4: acquisitions += enitity_donors
        else: acquisitions += 1
        
    return acquisitions, donors, objects


def plot(Xs, Ys, title="", color='b', savepath=""):
    sns.set_theme()
    plt.rcParams['font.family'] = "Source Serif 4, Source Serif Pro, Noto Serif"
    fig, ax = plt.subplots(figsize=(16,8))
    ax.bar(Xs, Ys, color=color)
    ax.set_title(title)
    
    if savepath: plt.savefig(savepath, bbox_inches='tight', format="pdf", dpi=300)
    plt.show()
    
    
if __name__ == "__main__":
    PICKLE_FILE = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotationsUnconsolidated.pickle"
    DIR_PATH = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/INCEpTION/UIMA_CAS_XMI"
    data = SemanticData(PICKLE_FILE, load=True)
    
    # Number of Entities and Properties:
    e_per_year = Counter(e.year for e in data.entities)
    p_per_year = Counter(p.source.year for p in data.properties)
    
    Xs = sorted(e_per_year)
    Ys = [e_per_year[y] for y in Xs]
    plot(Xs, Ys, title=f"Semantic Entities per year (sum = {sum(e_per_year.values())})", color="plum", savepath=f"../../Visualizations/Entities_per_year.pdf")
    
    Xs = sorted(p_per_year)
    Ys = [p_per_year[y] for y in Xs]
    plot(Xs, Ys, title=f"Semantic Properties per year (sum = {sum(p_per_year.values())})", color="cornflowerblue", savepath=f"../../Visualizations/Properties_per_year.pdf")

    mammalian_entities = find_mammalia_entities(data)

    acquisitions, donors, objects = count_acquisitions(mammalian_entities)
    print(f"Overall:\nNo. of Acquisitions: {acquisitions}, No. of donors: {donors}, No. of objects: {objects}")
    
    mammalian_entities_by_year = defaultdict(list)
    for e in mammalian_entities: mammalian_entities_by_year[e.year].append(e)
    
    Years = sorted(mammalian_entities_by_year)
    no_acq, no_donors, no_objects = [],[],[]
    print(f"|{'Year':<5}|{'No. of acquisitions':<5}|{'No. of collectors':<5}|{'No. of objects':<5}|")
    for year in Years:
        acquisitions, donors, objects = count_acquisitions(mammalian_entities_by_year[year])
        print(f"|{year:<5}|{acquisitions:<5}|{donors:<5}|{objects:<5}|")
        no_acq.append(acquisitions)
        no_donors.append(donors)
        no_objects.append(objects)
        
    colors = sns.color_palette("colorblind", 3)
    for i, (title, Xs, Ys) in enumerate(zip(("Approx. Number of Acquisitions", "Approx. Number of collectors", "Approx. Number of new objects"), (Years,Years,Years), (no_acq, no_donors, no_objects))):
        plot(Xs, Ys, title=title, color=colors[i], savepath=f"../../Visualizations/MammaliaStats{i}.pdf")
