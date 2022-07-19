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


def classifyProperty(prop, neighbor):
    if prop.short_type == "P43": return "Dimension"
    elif prop.short_type == "P130":  return "Taxon"
    elif neighbor.short_type == "E3":  return "Condition State/ Condition Assessement"
    elif neighbor.short_type == "E14":  return "Condition State/ Condition Assessement"
    elif neighbor.short_type == "E11":  return "Modification"
    elif prop.short_type == "P53":  return "Location"
    return None

def classifyAcquisition(e):
    if e.short_type == "E96": return "Purchase"
    assert e.short_type == "E8"
    
    for p in e.outgoing:
        if p.short_type == "P2": return p.target.string
    return "Unknown"
    
    
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
                elif p.target.short_type in ("E14","E3"): foundElements.add("Condition State/ Condition Assessement")
            for p in e.incoming:
                if p.source.short_type in ("E14","E3"): foundElements.add("Condition State/ Condition Assessement")
                    
            processed = set()
            while objs:
                obj = objs.popleft()
                if obj in processed: continue
                
                for p in obj.outgoing:
                    if p.short_type == "P46": objs.append(p.target)
                    elif (category := classifyProperty(p, p.target)): foundElements.add(category)
                for p in obj.incoming:
                    if p.short_type == "P46": objs.append(p.source)
                    elif (category := classifyProperty(p, p.source)): foundElements.add(category)
                processed.add(obj)
            result.update(foundElements)
    acquisitions_count = len(acquisitions)
    
    print(f"RESULT:\n    {len(entities)} Entities\n    {acquisitions_count} {acqType}Acquisitions")
    
    acquisitionsTypes = Counter([classifyAcquisition(e) for e in acquisitions])
    print("\nACQUISITION TYPES:")
    for element, count in acquisitionsTypes.most_common():
        if count > 1: print(f"    {element:<12} | {count:<10} | {round(count/acquisitions_count*100, 1)}%")
    
    acquisitionsPerYear = Counter([e.year for e in acquisitions])
    print(f"\nACQUISITIONS PER YEAR ({len(acquisitionsPerYear)} YEARS):")
    progressChar = '□'#'░' #one character in progress bar equals 10 acquisitions
    for year in sorted(acquisitionsPerYear.keys()):
        count = acquisitionsPerYear[year]
        bar = progressChar*int((count+9)/10)
        print(f"    {year:<4} | {count:>5} | {round(count/acquisitions_count*100, 1):>5}% | {bar:<100}")
    
    
    print("\nCONNECTED TYPES TO ACQUISITIONS:")
    for element, count in result.most_common():
        print(f"    {element:<40} | {count:<10} | {round(count/acquisitions_count*100, 1):>5}%")

if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)
    
    processDonations(data.entities, "")
    