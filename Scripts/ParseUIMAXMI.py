from collections import defaultdict
from bs4 import BeautifulSoup

class Anchors(object):
    def __init__(self):
        self.objs         = {} # string:Entity
        self.properties   = defaultdict(list) #string:[(property, target)]


class OCRCorrection(object):
    def __init__(self, tag, text):
        self.processed = False
        self.begin = int(tag["begin"])
        self.end = int(tag["end"])
        self.to_be_deleted = tag["Deletion"] == "true"
        if self.to_be_deleted:
            self.corrected_string = ""
            self.original_string = ""
        else:
            self.corrected_string = tag["CorrectedString"]
            self.original_string = text[self.begin:self.end]
    

class Corrector(object):
    def __init__(self, tags, text):
        self.corrections = sorted([OCRCorrection(tag, text) for tag in tags], key=lambda x: x.begin)
        self.offsets = {}
        self.text = text
        
    def __len__(self):
        return len(self.corrections)
    
    def apply(self, text):
        if not self.corrections:
            return self.text
        new_text = []
        cursor = 0
        accu = 0
        for correction in self.corrections:
            if correction.processed: continue
            if correction.to_be_deleted:
                accu += -1* (correction.end-correction.begin)
                self.offsets[correction.end] = accu
                new_text.append(text[cursor:correction.begin])
                cursor = correction.end
                
            else:
                accu += len(correction.corrected_string)-len(correction.original_string)
                self.offsets[correction.end] = accu
                new_text.append(text[cursor:correction.begin])
                new_text.append(correction.corrected_string)
                cursor = correction.end
                
            correction.processed = True
        new_text.append(text[cursor:])
        #print(self.offsets)
        self.text = ''.join(new_text)
        return self.text
    
    def offset(self, index):
        cursor = index
        if self.offsets and cursor < len(self.text):
            while 0 <= cursor:
                if cursor in self.offsets: return self.offsets[cursor] + index
                cursor -= 1
        return index
            


class SemanticEntity(object):
    virtuals = []
    next_id  = 0
    def __init__(self, tag, corrector, anchors=None, virtual=False):
        ''''''
        self.id = self.next_id
        SemanticEntity.next_id += 1
        
        self.type = tag["SemanticClass"]
        self.incoming = []
        self.outgoing = []
        
        if virtual:
            self.original_id = None
            self.virtual     = True
            self.begin       = None
            self.end         = None
            self.string      = tag["string"]
            SemanticEntity.virtuals.append(self)
        else:
            self.original_id = int(tag["xmi:id"])
            maske = False
            if tag.has_attr("Postprocessing"):
                maske = parse_postprocessing(tag['Postprocessing'], self, anchors)
            
            if maske:
                self.virtual     = True
                self.begin       = None
                self.end         = None
                self.string      = "(implicit) Unknown"
            else:
                self.virtual     = False
                self.begin       = corrector.offset(int(tag["begin"]))
                self.end         = corrector.offset(int(tag["end"]))
                self.string      = corrector.text[self.begin:self.end]



    
    def __str__(self):
        return f"{self.type}: '{self.string}'"



class SemanticProperty(object):
    virtuals = []
    next_id  = 0
    def __init__(self, tag, entity_map=None, virtual=False, source=None, target=None):
        self.id = self.next_id
        SemanticProperty.next_id += 1
        
        if virtual:
            assert isinstance(source, SemanticEntity) and isinstance(target, SemanticEntity)
            self.type        = tag["SemanticProperty"]
            self.original_id = None
            
            self.source_id = source.original_id
            self.source    = source

            self.target_id = target.original_id
            self.target    = target
            
            self.source.outgoing.append(self)
            self.target.incoming.append(self)
            
            
            
            SemanticProperty.virtuals.append(self)
        else:
            self.original_id = int(tag["xmi:id"])
            self.type        = tag["SemanticProperty"]
            self.source_id   = int(tag["Governor"])
            self.target_id   = int(tag["Dependent"])
            
            if entity_map:
                self.source = entity_map[self.source_id]
                self.target = entity_map[self.target_id]
                
                self.source.outgoing.append(self)
                self.target.incoming.append(self)
            else:
                self.source = None
                self.target = None
    
    def __str__(self):
        if self.source: return f"{self.source} → {self.type} → {self.target}"
        return f"{self.source_id} → {self.type} → {self.target_id}"

def parse_postprocessing(tag_string, source, anchors):
    #print(f"Parsing post for {str(source)}")
    
    maske = False
    for info in tag_string.split('|'):
        lowered_info = info.lower()
        if lowered_info == "virtual":
            maske = True
            continue
        
        
        if lowered_info.startswith('!'): inverse = True
        else: inverse = False
        
        if "anchor" in lowered_info:
            if lowered_info.count(':'):
                double = info.split(':')
                assert len(double) == 2
                
                anchors.properties[double[1].lower()].append((double[0],source))
            else:
                # source ist selbst ein Anchor
                anchors.objs[lowered_info] = source
            continue
                
        else:
            triple = info.lstrip('!').split(':')
            assert len(triple) == 3
        
        if inverse:
            target = SemanticEntity({'SemanticClass':triple[1],'string':f"{triple[2]}"}, None, virtual=True)
            property = SemanticProperty({"SemanticProperty":triple[0]}, virtual=True, source=target, target=source)
        else:
            target = SemanticEntity({'SemanticClass':triple[1],'string':triple[2]}, None, virtual=True)
            property = SemanticProperty({"SemanticProperty":triple[0]}, virtual=True, source=source, target=target)
        
    return maske

def set_anchors(anchors):
    for anchor_str, anchor in anchors.objs.items():
        for double in anchors.properties[anchor_str]:
            if double[0].startswith('!'):
                property = SemanticProperty({"SemanticProperty":double[0].lstrip('!')}, virtual=True, source=anchor, target=double[1])
            else:
                property = SemanticProperty({"SemanticProperty":double[0]}, virtual=True, source=double[1], target=anchor)


def parse(filepath):
    '''returns (Corrected Text: string, Semantic Entities: list, Semantic Properties: list with Pointers to objects in Entities list)'''
    
    print(f"Parsing {filepath}:")
    with open(filepath, 'r', encoding="utf-8") as f:
        xml = BeautifulSoup(f, "xml")
    
    text = xml.find("cas:Sofa")["sofaString"]
    corrector = Corrector(xml.find_all("custom:OCRCorrection"), text)
    text = corrector.apply(text)
    print(f"    Applied {len(corrector)} OCR-Corrections")
    
    anchors = Anchors()
    
    entities = [SemanticEntity(tag, corrector, anchors) for tag in xml.find_all("custom:SemanticEntities")]
    print(f"    Parsed {len(entities)} original and {len(SemanticEntity.virtuals)} virtual Entities")
    entities += SemanticEntity.virtuals
    
    set_anchors(anchors)
    entity_map = {e.original_id:e for e in entities}
    properties = [SemanticProperty(tag, entity_map) for tag in xml.find_all("custom:SemanticRelations")]
    print(f"    Parsed {len(properties)} original and {len(SemanticProperty.virtuals)} virtual Properties")
    properties += SemanticProperty.virtuals
    
    return text, entities, properties

if __name__ == "__main__":
    TEST_FILE = "C:/Users/Aron/Downloads/webanno5422277547538360861export/1889_Zoologische_140-144.xmi"#"C:/Users/Aron/Downloads/webanno17844155560286750721export/1889_Geologisch-paläontologische_137-138.xmi"#"C:/Users/Aron/Downloads/webanno3163352340135431318export/1887_Museum_67-67.xmi"
    text, entities, properties = parse(TEST_FILE)
    print(text, '\n')
    
    print("\n".join([str(e) for e in properties]))

