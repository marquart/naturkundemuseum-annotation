import os
from collections import defaultdict, Counter, deque 

from SemanticModels import SemanticEntity, SemanticProperty, SemanticData


def is_museums_collection(e):
    if e.short_type == "E78":
        for p in e.incoming:
            if p.short_type == "P22": return True
    return False
    
    
def validAcquisition(e, type=""):
    if e.short_type not in ("E8","E96"): return False
    
    museum_acquisition, correct_type = False, type == ""
    for p in e.outgoing:
        if p.short_type in ("P22","P23") and not museum_acquisition:
            museum_acquisition = is_museums_collection(p.target)
        elif p.short_type == "P2" and not correct_type:
            correct_type = p.target.string == type
    return museum_acquisition and correct_type
    

def calculateWeight(e):
    ''' e.short_type == Acquisition or Purchase
    '''
    assert e.short_type in ("E8","E96")
    validTypes = {
        "E53":1, #Place
        "E19":1, #Physical Object
        "E20":1, #Bio Object
        "E78":1, #Holding
        "E28":2, #Concept
        "E54":1, #Place
        "E39":1, #Actor
        "E21":1, #Person
        "E74":1, #Group
        "E3" :2, #Condition State/
        "E14":2, #Condition Assessment
        "E11":2, #Modification
        "E54":2, #Dimension
        "E60":2, #Number
    }
    stopProperties = {
        "E8": (),
        "E96":(),
        "E53":("P1","P2","P22","P53"), #Place
        "E19":("P1","P2","P22"), #Physical Object
        "E20":("P1","P2","P22"), #Bio Object
        "E78":("P1","P2","P22","P46"), #Holding
        "E28":("P1","P2","P22","P130"), #Concept
        "E54":("P1","P2","P22"), #Place
        "E39":("P1","P2","P22","P23"), #Actor
        "E21":("P1","P2","P22","P23"), #Person
        "E74":("P1","P2","P22","P23"), #Group
        "E3" :("P1","P2","P22"), #Condition State/
        "E14":("P1","P2","P22"), #Condition Assessment
        "E11":("P1","P2","P22"), #Modification
        "E54":("P1","P2","P22","P43"), #Dimension
        "E60":("P1","P2","P22"), #Number
    }
    
    stack = deque((e,))
    processed = set()
    weight = 0
    while stack:
        cursor = stack.popleft()
        if cursor in processed: continue
        processed.add(cursor)
        for p in cursor.incoming:
            if p.source in processed: continue
            if p.source.short_type in validTypes:
                if p.short_type in stopProperties[cursor.short_type]: continue
                if not p.source.virtual:
                    weight += validTypes[p.source.short_type]
                    if e.id == 29472 or e.id == 16277:
                        print(f"    {weight} | Added {p.source.verbose()}")
                        print(f"         <-- {p.short_type} <-- {cursor.verbose()}")
                stack.append(p.source)
        for p in cursor.outgoing:
            if p.target in processed: continue
            if p.target.short_type in validTypes:
                if p.short_type in stopProperties[cursor.short_type]: continue
                if not p.target.virtual:
                    weight += validTypes[p.target.short_type]
                    if e.id == 29472 or e.id == 16277:
                        print(f"    {weight} | Added {p.target.verbose()}")
                        print(f"         --> {p.short_type} --> {cursor.verbose()}")
                stack.append(p.target)
    return weight

def calculateWeights(entities):
    weights = {}
    for e in entities:
        if validAcquisition(e):
            w = calculateWeight(e)
            if w>9: w = 10
            weights[e.id] = w
    return weights

if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)
    weights = Counter()
    for e in data.entities:
        if validAcquisition(e):
            w = calculateWeight(e)
            if w>9: w = 10
            weights[w] += 1
            if w>50: print(e.verbose())
    print(f"Calculated weights for {sum(weights.values())} acquisitions:")
    for w in sorted(weights.keys()):
        print(f"    {w:<5} weight | {weights[w]:<5} acquisitions | {round(weights[w]/sum(weights.values())*100, 1)}%")

    
    