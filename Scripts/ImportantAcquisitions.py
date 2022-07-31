import os
from collections import defaultdict, Counter, deque 

from matplotlib.colors import LinearSegmentedColormap, to_hex

from SemanticModels import SemanticEntity, SemanticProperty, SemanticData


class Acquisition(object):
    cmap = LinearSegmentedColormap.from_list("cmap", ("#c7df7f", "#7da30b"), N=10)
    
    def __init__(self, e, acquisitionsWeights=None):
        assert e.short_type in ("E8","E96")
        
        self.entity     = e
        self.holding    = None
        self.locations  = []
        self.givers     = []
        self.category   = None
        self.neighbors  = set()

        if acquisitionsWeights:
            self.weight = acquisitionsWeights[e.id]
        else:
            self.weight, self.neighbors = calculateWeight(e, return_stack=True)

        self.color      = to_hex(Acquisition.cmap(self.weight))
        
        for p in e.outgoing:
            if p.short_type == "P22":
                self.holding = p.target
            elif p.short_type == "P23":
                self.givers.append(p.target)
            elif p.short_type == "P24":
                stack = deque((p.target,))
                while stack:
                    cursor = stack.popleft()
                    for pp in cursor.outgoing:
                        if pp.short_type == "P53":
                            self.locations.append(pp.target)
                        elif pp.short_type == "P46":
                            stack.append(pp.target)
            elif p.short_type == "P2":
                self.category = p.target.string


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
    

def calculateWeight(e, return_stack=False):
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
        "E39":("P1","P2","P22","P23"), #Actor
        "E21":("P1","P2","P22","P23"), #Person
        "E74":("P1","P2","P22","P23"), #Group
        "E3" :("P1","P2","P22"), #Condition State/
        "E14":("P1","P2","P22"), #Condition Assessment
        "E11":("P1","P2","P22"), #Modification
        "E54":("P1","P2","P22","P43"), #Dimension
        "E60":("P1","P2","P22"), #Number
    }
    stopNeighbors = {
        "E3":  ("E78",),      #Condition State of receiving collection
        "E78":  ("E3","E14"), #Condition State of receiving collection
        "E14": ("E78",),      #Condition Assessment of receiving collection
    }
    
    stack = deque((e,))
    processed = set()
    weight = 0
    foundAssessment = False
    while stack:
        cursor = stack.popleft()
        if cursor in processed: continue
        processed.add(cursor)
        for p in cursor.incoming:
            if p.source in processed: continue
            if p.source.short_type in validTypes:
                if p.short_type in stopProperties[cursor.short_type]: continue
                if cursor.short_type in stopNeighbors and p.source.short_type in stopNeighbors[cursor.short_type]: continue
                if not p.source.virtual:
                    weight += validTypes[p.source.short_type]
                    if p.source.short_type in ("E3","E14"): foundAssessment = True
                stack.append(p.source)
        for p in cursor.outgoing:
            if p.target in processed: continue
            if p.target.short_type in validTypes:
                if p.short_type in stopProperties[cursor.short_type]: continue
                if cursor.short_type in stopNeighbors and p.target.short_type in stopNeighbors[cursor.short_type]: continue
                if not p.target.virtual:
                    weight += validTypes[p.target.short_type]
                    if p.target.short_type in ("E3","E14"): foundAssessment = True
                stack.append(p.target)
    if foundAssessment: weight = MAX_WEIGHT
    elif weight >= MAX_WEIGHT: weight = MAX_WEIGHT-1

    if return_stack: return weight, processed
    return weight


def calculateWeights(entities):
    weights = {}
    for e in entities:
        if validAcquisition(e):
            w = calculateWeight(e)
            if w>MAX_WEIGHT: w = 10
            weights[e.id] = w
    return weights


def findAcquisitions(entities):
    acquisitions = []
    for e in entities:
        if validAcquisition(e):
            acquisitions.append(Acquisition(e))
    return acquisitions

def createSVG(shareOfWeights):
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid") #style='white'
    plt.rcParams['font.sans-serif'] = "Roboto, sans-serif"
    plt.rcParams['font.family'] = "Roboto,"
    plt.rcParams['svg.fonttype'] = 'none'

    fig, ax = plt.subplots(figsize=(11.69,4))

    xs = sorted(shareOfWeights)
    for i,weight in enumerate(xs):
        share = shareOfWeights[weight]
        color = Acquisition.cmap(i)
        ax.bar(weight, share, color=color, ecolor="#000000")
        ax.annotate(f"{round(share,1)}%", (weight, share), xytext=(weight-.55, share+8.), arrowprops=dict(arrowstyle="->",color="0.2",patchB=None,shrinkB=0,connectionstyle="arc3,rad=-0.3",))


    ax.set_ylabel("Percentage of all acquisitions")
    ax.set_xticks(xs)
    ax.set_xticklabels(xs)
    ax.set_xlabel("Weight")
    sns.despine(top=True, bottom=True, left=True, right=True)
    plt.savefig("../Documentation/Visualizations/AcquisitionsWeights.svg", dpi=300, bbox_inches='tight', format='svg', transparent=True)
    print("Saved visualization '../Documentation/Visualizations/AcquisitionsWeights.svg'")

MAX_WEIGHT = 10

if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)
    weights = Counter([a.weight for a in findAcquisitions(data.entities)])
    progressChar = '□'#'░' #one character in progress bar equals 40 acquisitions

    shareOfWeights = {}
    print(f"Calculated weights for {sum(weights.values())} acquisitions:")
    totalAcquisitions = sum(weights.values())
    for w in sorted(weights.keys()):
        count = weights[w]
        share = count/totalAcquisitions*100
        shareOfWeights[w] = share
        bar = progressChar*int((count+39)/40)
        print(f"    {w:>2} weight | {count:<5} acquisitions | {round(share, 1):>4}% | {bar:<140}")
    
    createSVG(shareOfWeights)

    
    