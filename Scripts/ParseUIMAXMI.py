from bs4 import BeautifulSoup

class OCRCorrection(object):
    def __init__(self, tag):
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
    def __init__(self, tags):
        self.corrections = sorted([OCRCorrection(tag) for tag in tags], key=lambda x: x.begin)
        self.offsets = {}
    
    def build_offset(self, text):
        if not self.corrections: return text
        new_text = []
        cursor = 0
        for correction in self.corrections:
            if correction.processed: continue
            if correction.to_be_deleted:
                self.offsets[correction.end] = -1* (correction.end-correction.begin)
                new_text.append(text[cursor:correction.begin])
                cursor = correction.end
                
            else:
                self.offsets[correction.end] = len(correction.corrected_string)-len(correction.original_string)
                new_text.append(text[cursor:correction.begin])
                new_text.append(correction.corrected_string)
                cursor = correction.end
                
            correction.processed = True
        print(self.offsets)
        return ''.join(new_text)
    
    def offset(self, index):
        cursor = index
        if self.offsets:
            while 0 <= cursor < len(text):
                if cursor in self.offsets: return self.offsets[cursor] + index
                cursor -= 1
        return index
            


class SemanticEntity(object):
    def __init__(self, tag, corrector):
        self.id = int(tag["xmi:id"])
        self.type = tag["SemanticClass"]
        self.begin = corrector.offset(int(tag["begin"]))
        self.end = corrector.offset(int(tag["end"]))
        self.string = text[self.begin:self.end]
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

    

if __name__ == "__main__":
    TEST_FILE = "C:/Users/Aron/Downloads/webanno5013015553902450731export/1887_Museum_67-67.xmi"
    
    with open(TEST_FILE, 'r', encoding="utf-8") as f:
        xml = BeautifulSoup(f, "xml")
    
    text = xml.find("cas:Sofa")["sofaString"]
    corrector = Corrector(xml.find_all("custom:OCRCorrection"))
    text = corrector.build_offset(text)
    print(text, '\n')
    
    entities = [SemanticEntity(tag, corrector) for tag in xml.find_all("custom:SemanticEntities")]
    entity_map = {e.id:e for e in entities}
    properties = [SemanticProperty(tag, entity_map) for tag in xml.find_all("custom:SemanticRelations")]
    
    
    print("\n".join([str(e) for e in properties]))

