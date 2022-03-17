import re
from collections import defaultdict, Counter

from ParseUIMAXMI import SemanticEntity, SemanticProperty, SemanticData

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
    
    
    general_types = Counter()
    types = Counter()
    for e in data.entities:
        class_ = e.short_type
        if class_ in REVERSE_LOOKUP:
            general_types[REVERSE_LOOKUP[class_]] += 1
            types[class_] += 1
        
        if e.virtual and class_ in ("E78","E21","E53","E28","E74"):
            print(e.short_type, e.id, e.year, e.institution)
    
    palette = sns.color_palette('pastel', 10)
    palette[7] = palette[9]
    general_colors = {t[0]:to_hex(palette[i]) for i,t in enumerate(general_types.most_common())}
    colors = {t: general_colors[REVERSE_LOOKUP[t]] for t in types}
    
    print(colors)
  
    

    
