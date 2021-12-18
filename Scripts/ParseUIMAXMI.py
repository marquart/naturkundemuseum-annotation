from bs4 import BeautifulSoup

class OCRCorrection(object):
    def __init__(self, tag, text):
        self.processed = False
        self.begin = int(tag["begin"])
        self.end = int(tag["end"])
        self.to_be_deleted = True if tag["Deletion"] == "true" else False
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
    def __init__(self, tag, corrector):
        self.id = int(tag["xmi:id"])
        self.type = tag["SemanticClass"]
        self.begin = corrector.offset(int(tag["begin"]))
        self.end = corrector.offset(int(tag["end"]))
        self.string = corrector.text[self.begin:self.end]
        self.incoming = []
        self.outgoing = []
    
    def __str__(self):
        return f"{self.type}: '{self.string}'"



class SemanticProperty(object):
    def __init__(self, tag, entity_map=None):
        self.id = int(tag["xmi:id"])
        self.type = tag["SemanticProperty"]
        self.source_id = int(tag["Governor"])
        self.target_id = int(tag["Dependent"])
        
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

def parse(filepath):
    '''returns (Corrected Text: string, Semantic Entities: list, Semantic Properties: list with Pointers to objects in Entities list)'''
    
    print(f"Parsing {filepath}:")
    with open(filepath, 'r', encoding="utf-8") as f:
        xml = BeautifulSoup(f, "xml")
    
    text = xml.find("cas:Sofa")["sofaString"]
    corrector = Corrector(xml.find_all("custom:OCRCorrection"), text)
    text = corrector.apply(text)
    print(f"    Applied {len(corrector)} OCR-Corrections")
    
    entities = [SemanticEntity(tag, corrector) for tag in xml.find_all("custom:SemanticEntities")]
    print(f"    Parsed {len(entities)} Entities")
    
    entity_map = {e.id:e for e in entities}
    properties = [SemanticProperty(tag, entity_map) for tag in xml.find_all("custom:SemanticRelations")]
    print(f"    Parsed {len(properties)} Properties")
    
    return text, entities, properties

if __name__ == "__main__":
    TEST_FILE = "C:/Users/Aron/Downloads/webanno5013015553902450731export/1887_Museum_67-67.xmi"
    
    text, entities, properties = parse(TEST_FILE)
    print(text, '\n')
    
    print("\n".join([str(e) for e in properties]))

