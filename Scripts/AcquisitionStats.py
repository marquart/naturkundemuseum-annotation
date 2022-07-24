from html import entities
import os
from collections import defaultdict, Counter, deque

from SemanticModels import SemanticEntity, SemanticProperty, SemanticData

import matplotlib.pyplot as plt
import seaborn as sns


def renderAcquisitionsPerYear(acquisitionsPerYear):
    sns.set_theme(style="whitegrid") #style='white'
    plt.rcParams['font.sans-serif'] = "Roboto, sans-serif"
    plt.rcParams['font.family'] = "Roboto,"
    plt.rcParams['svg.fonttype'] = 'none'

    fig, ax = plt.subplots(figsize=(11.69,4))

    for year in sorted(acquisitionsPerYear):
        if year>1916: break
        count = acquisitionsPerYear[year]
        ax.bar(year, count, color="#fc3915", ecolor="#000000")
    ax.set_ylabel("No. of acquisitions")
    ax.set_xlabel("Years")
    sns.despine(top=True, bottom=True, left=True, right=True)
    plt.savefig("../Documentation/Visualizations/AcquisitionsPerYear.svg", dpi=300, bbox_inches='tight', format='svg', transparent=True)
    print("Saved visualization '../Documentation/Visualizations/AcquisitionsPerYear.svg'")



def count_lines(data):
    complete_lines = 0
    for txt in data.texts:
        complete_lines += len(txt['Lines'])
    
    annotetdLinesPerTXT = defaultdict(set)
    for e in data.entities:
        if not e.virtual: annotetdLinesPerTXT[e.txt_id].add(e.line_idx)

    annotated_lines = sum([len(s) for s in annotetdLinesPerTXT.values()])
    return complete_lines, annotated_lines


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
    elif neighbor.short_type == "E3":  return "Condition State/ Condition Assessment"
    elif neighbor.short_type == "E14":  return "Condition State/ Condition Assessment"
    elif neighbor.short_type == "E11":  return "Modification"
    elif prop.short_type == "P53":  return "Location"
    return None

def classifyAcquisition(e):
    if e.short_type == "E96": return "Purchase"
    assert e.short_type == "E8"
    
    for p in e.outgoing:
        if p.short_type == "P2": return p.target.string
    return "Unknown"
    
    
def processDonations(data, acqType):
    entities = data.entities
    classes = ("Recipient","Giver","Object(s)","Dimension","Taxon","Condition State/ Condition Assessment","Modification","Location")
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
                elif p.target.short_type in ("E14","E3"): foundElements.add("Condition State/ Condition Assessment")
            for p in e.incoming:
                if p.source.short_type in ("E14","E3"): foundElements.add("Condition State/ Condition Assessment")
                    
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
    
    allLines, annotatedLines = count_lines(data)
    print(f"RESULT:\n    {allLines} Lines\n    {annotatedLines} annotated Lines")


    print(f"\n    {len(entities)} Entities\n    {acquisitions_count} {acqType}Acquisitions")
    
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
    
    renderAcquisitionsPerYear(acquisitionsPerYear)
    
    print("\nCONNECTED TYPES TO ACQUISITIONS:")
    for element, count in result.most_common():
        print(f"    {element:<40} | {count:<10} | {round(count/acquisitions_count*100, 1):>5}%")

if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)
    
    processDonations(data, "")
    