from collections import Counter, defaultdict

from ParseUIMAXMI import SemanticData, SemanticEntity, SemanticProperty

if __name__ == "__main__":
    PICKLE_FILE = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    data = SemanticData(PICKLE_FILE, load=True)
    
    virtual_entities = defaultdict(Counter)
    for e in data.entities:
        label = f"{e.year}_{e.institution}"
        virtual_entities[label][e.virtual] += 1
    
    max_share = 0.
    for label, countr in virtual_entities.items():
        virtual_share = round(countr[True]/sum(countr.values())*100, 2)
        print(f"{label:<90}: {virtual_share:>7}% virtual entities")
        if virtual_share>max_share: max_share = virtual_share
    print("Max share: ", max_share)
    
    count = 0
    for e in data.entities:
        if e.year == 1898 and e.page == 134 and e.line in (12,13,14,15):
            count += 1
    print(count)
    
    
