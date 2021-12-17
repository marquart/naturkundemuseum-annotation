import os

from bs4 import BeautifulSoup

class SemanticEntity(object):
    def __init__(self, tag):
        self.id = int(tag["xmi:id"])
        self.type = tag["SemanticClass"]
        self.begin = int(tag["begin"])
        self.end = int(tag["end"])
        self.string = text[self.begin:self.end]
        self.incoming = []
        self.outgoing = []
    
    def __str__(self):
        return f"{self.type}: {self.string}"



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
    entities = [SemanticEntity(tag) for tag in xml.find_all("custom:SemanticEntities")]
    entity_map = {e.id:e for e in entities}
    properties = [SemanticProperty(tag, entity_map) for tag in xml.find_all("custom:SemanticRelations")]
    
    
    print("\n".join([str(e) for e in properties]))

