import re
from collections import defaultdict, Counter

from ParseUIMAXMI import SemanticEntity, SemanticProperty
from CollectionStats import SemanticData

from matplotlib.colors import to_hex
import seaborn as sns

if __name__ == "__main__":
    PICKLE_FILE = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle"
    data = SemanticData(PICKLE_FILE, load=True)
    LOOKUP = {
        "E53": ("E53",), #Place
        "E2" : ("E2","E54","E52","E3","E63"), #Dimension/Time Entity/Condition
        "E39": ("E39","E21", "E74"), #Actor
        "E7" : ("E7","E8","E96","E87","E85","E86","E9","E14","E11","E79","E12","E66"), # Activity
        "E28": ("E28","E55"), #Conceptual
        "E90": ("E90","E41","E35","E42","E29","E73","E60"), #Symbolic/Information Object
        "E78": ("E78","E77"), # Holding/Human-Made
        "E18": ("E18","E20","E19","E57"), #Physical Thing
    }
    REVERSE_LOOKUP = {vv:k for k,v in LOOKUP.items() for vv in v}
    
    CLASS_PATTERN = re.compile(r"^(E\d+?) ")
    
    general_types = Counter()
    types = Counter()
    for e in data.entities:
        class_ = CLASS_PATTERN.search(e.type).group(1)
        if class_ in REVERSE_LOOKUP:
            general_types[REVERSE_LOOKUP[class_]] += 1
            types[class_] += 1
    
    palette = sns.color_palette('muted', len(LOOKUP))
    general_colors = {t[0]:to_hex(palette[i]) for i,t in enumerate(general_types.most_common())}
    colors = {t: general_colors[REVERSE_LOOKUP[t]] for t in types}
    
    print(colors)
    

    
