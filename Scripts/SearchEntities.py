import pickle
from itertools import chain
from collections import defaultdict
import argparse

from ParseUIMAXMI import SemanticEntity, SemanticProperty


class Searcher(object):
    def __init__(self, datafile):
        data = load_pickle(datafile)
        self.lookup = defaultdict(list)
        for e in chain.from_iterable([doc["Entities"].values() for doc in data]):
            self.lookup[clean(e.string).lower()].append(e)
    
    def pprint(self, entity):
        return f"{entity.type:<24}: '{clean(entity.string):<90}' ({entity.id:<5}| {entity.institution:<50} {entity.year:<4})"
    
    def search(self, search_string, _type=None):
        assert type(search_string) is str
        
        print(f"Results in Entities for '{search_string}':")
        search_string = search_string.lower()
        for e_string, entities in self.lookup.items():
            if search_string in e_string:
                if _type:
                    print('\n'.join(self.pprint(e) for e in entities if _type in e.type))
                else:
                    print('\n'.join(self.pprint(e) for e in entities))


def clean(txt):
    return txt.replace('\r\n', ' ').replace('\n', ' ').replace('‑', '').replace('-', '')

def load_pickle(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data
    
def search(datafile, entity_string):
    data = load_pickle(datafile)
    lookup = defaultdict(list)
    for e in chain.from_iterable([doc["Entities"].values() for doc in data]): lookup[clean(e.string)].append(e)
    result = [lookup[e_string] for e_string in lookup if entity_string in e_string]
    
    print('\n'.join([e.verbose() for e in chain.from_iterable(result)]))

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', '-t')
    parser.add_argument("search_string", type=str, default='')
    
    pickle_file = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    searcher = Searcher(pickle_file)
    args = parser.parse_args()
    if args.search_string: searcher.search(args.search_string, _type=args.type)
    else: searcher.search("British")
