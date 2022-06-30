import os
from collections import defaultdict, Counter, deque

from SemanticModels import SemanticEntity, SemanticProperty, SemanticData


def is_museums_collection(e):
    if e.short_type == "E78":
        for p in e.incoming:
            if p.short_type == "P22": return True
    return False
    
    
def validAcquisition(e, type):
    if e.short_type not in ("E8","E96"): return False
    
    museum_acquisition, correct_type = False, type == ""
    for p in e.outgoing:
        if p.short_type in ("P22","P23") and not museum_acquisition:
            museum_acquisition = is_museums_collection(p.target)
        elif p.short_type == "P2" and not correct_type:
            correct_type = p.target.string == type
    return museum_acquisition and correct_type
    

def processDonations(entities, acqType):
    classes = ("Recipient","Giver","Object(s)","Dimension","Taxon","Condition State/ Condition Assessement","Modification","Location")
    result = Counter()
    acquisitions = []
    for e in entities:
        if validAcquisition(e, acqType):
            acquisitions.append(e)
            
            foundElements = set()
            objs = deque()
            for p in e.outgoing:
                if p.short_type == "P22": foundElements.add("Recipient")
                elif p.short_type == "P23": foundElements.add("Giver")
                elif p.short_type == "P24":
                    foundElements.add("Object(s)")
                    objs.append(p.target)
                    
            processed = set()
            while objs:
                obj = objs.popleft()
                if obj in processed: continue
                
                for p in obj.outgoing:
                    if p.short_type == "P46": objs.append(p.target)
                    elif p.short_type == "P43": foundElements.add("Dimension")
                    elif p.short_type == "P130": foundElements.add("Taxon")
                    elif p.target.short_type == "E3": foundElements.add("Condition State/ Condition Assessement")
                    elif p.target.short_type == "E14": foundElements.add("Condition State/ Condition Assessement")
                    elif p.target.short_type == "E11": foundElements.add("Modification")
                    elif p.short_type == "P53": foundElements.add("Location")
                for p in obj.incoming:
                    if p.short_type == "P46": objs.append(p.source)
                    elif p.short_type == "P43": foundElements.add("Dimension")
                    elif p.short_type == "P130": foundElements.add("Taxon")
                    elif p.source.short_type == "E3": foundElements.add("Condition State/ Condition Assessement")
                    elif p.source.short_type == "E14": foundElements.add("Condition State/ Condition Assessement")
                    elif p.source.short_type == "E11": foundElements.add("Modification")
                    elif p.short_type == "P53": foundElements.add("Location")
                processed.add(obj)
            result.update(foundElements)
    acquisitions_count = len(acquisitions)
    print(f"RESULT:\n{acquisitions_count} {acqType} Acquisitions")
    for element, count in result.most_common():
        print(f"{element:<60} | {count:<10} | {round(count/acquisitions_count*100, 2)}%")

if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)
    processDonations(data.entities, "")
    