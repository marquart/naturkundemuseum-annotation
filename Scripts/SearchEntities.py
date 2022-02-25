import pickle
from itertools import chain
from collections import defaultdict
from ParseUIMAXMI import SemanticEntity, SemanticProperty


class Searcher(object):
    def __init__(self, datafile):
        data = load_pickle(datafile)
        self.lookup = defaultdict(list)
        for e in chain.from_iterable([doc["Entities"].values() for doc in data]):
            self.lookup[clean(e.string)].append(e)
    
    def search(self, search_string):
        assert type(search_string) is str
        print(f"Results in Entities for '{search_string}':")
        for e_string, entities in self.lookup.items():
            if search_string in e_string:
                print('\n'.join([e.verbose() for e in entities]))


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
    pickle_file = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    searcher = Searcher(pickle_file)
    searcher.search("British")
