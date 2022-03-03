import os
from collections import defaultdict, Counter
from operator import attrgetter
import json, re
import pickle
from bs4 import BeautifulSoup
from bs4.element import Tag as BS4_TAG

class Anchors(object):
    def __init__(self):
        self.objs         = {} # string:Entity
        self.properties   = defaultdict(list) #string:[(property, target)]


class OCRCorrection(object):
    def __init__(self, tag, text):
        self.processed     = False
        self.begin         = int(tag["begin"])
        self.end           = int(tag["end"])
        self.to_be_deleted = tag["Deletion"] == "true"
        
        if self.to_be_deleted:
            self.corrected_string = ""
            self.original_string  = ""
        else:
            self.corrected_string = tag["CorrectedString"]
            self.original_string  = text[self.begin:self.end]
    

class Corrector(object):
    def __init__(self, tags, text):
        self.corrections = sorted([OCRCorrection(tag, text) for tag in tags], key=attrgetter('begin'))
        self.offsets     = {}
        self.text        = text
        self.pagenumbers = {}
        self.linenumbers = {}
        self.cleaner     = str.maketrans("\n", " ", "\r‑-­")
        
    def __len__(self):
        return len(self.corrections)
    
    def apply(self, text):
        if not self.corrections:
            self.set_pagenumbers()
            self.set_linenumbers()
            return self.text
        new_text = []
        cursor   = 0
        accu     = 0
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
        self.set_pagenumbers()
        self.set_linenumbers()
        return self.text
    
    def clean(self, txt):
        #return txt.replace('\r\n', ' ').replace('\n', ' ').replace('‑', '').replace('-', '').replace('­', '')
        return txt.strip().translate(self.cleaner)
    
    def set_pagenumbers(self):
        BEGIN_PATTERN = re.compile(r"====PAGEBEGIN (\d+?)====\r?\n")
        BREAK_PATTERN = re.compile(r"====PAGEBREAK TO (\d+?)====\r?\n")
        begin = BEGIN_PATTERN.search(self.text)
        self.pagenumbers[begin.end()] = int(begin.group(1))
        for match in BREAK_PATTERN.finditer(self.text):
            self.pagenumbers[match.end()] = int(match.group(1))

        
    def set_linenumbers(self):
        LINEBREAK_PATTERN = re.compile('\n|­')
        for i, match in enumerate(LINEBREAK_PATTERN.finditer(self.text), start=2):
            self.linenumbers[match.start()] = i
        
    def get_pagenumber(self, index):
        cursor = index
        if self.pagenumbers:
            while 0 <= cursor:
                if cursor in self.pagenumbers: return self.pagenumbers[cursor]
                cursor -= 1
        return -1
    
    def get_linenumber(self, index):
        cursor = index
        if self.linenumbers:
            while 0 <= cursor:
                if cursor in self.linenumbers: return self.linenumbers[cursor]
                cursor -= 1
        return -1
        
    def offset(self, index):
        cursor = index
        if self.offsets:
            while 0 <= cursor:
                if cursor in self.offsets:
                    assert self.offsets[cursor] + index < len(self.text)
                    return self.offsets[cursor] + index
                cursor -= 1
        return index
            


class SemanticEntity(object):
    virtuals = []
    next_id  = 0
    def __init__(self, tag, corrector, anchors=None, virtual=False, year=None, institution=None):
        ''''''
        self.id = self.next_id
        self.processed = False # Variable which can be used in recursion algorithms, USE WITH CAUTION
        SemanticEntity.next_id += 1
        
        self.year = year
        self.institution = institution
        
        if not check_property_exists(tag, "SemanticClass"): self.type = "E0 Unknown"
        else: self.type = tag["SemanticClass"].strip()
        self.incoming = []
        self.outgoing = []
        
        if virtual:
            self.original_id = f"V{self.id}"
            self.virtual     = True
            self.begin       = None
            self.end         = None
            self.string      = corrector.clean(tag["string"])
            self.page        = -1
            self.line        = -1
            SemanticEntity.virtuals.append(self)
        else:
            self.original_id = int(tag["xmi:id"])
            virtual_from_source = False
            
            char_begin = int(tag["begin"])
            char_end = int(tag["end"])
            
            if tag.has_attr("Postprocessing"):
                virtual_from_source = parse_postprocessing(tag['Postprocessing'], self, anchors, corrector)
                
            if not virtual_from_source and check_property_exists(tag, "Virtual"):
                virtual_from_source = tag["Virtual"] == "true"
            
            if virtual_from_source:
                self.virtual = True
                self.begin   = None
                self.end     = None
                self.string  = "(implicit) Unknown"
                self.page    = corrector.get_pagenumber(char_begin)
                self.line    = corrector.get_linenumber(char_begin)
            else:
                self.virtual = False
                self.begin   = corrector.offset(char_begin)
                self.end     = corrector.offset(char_end)
                self.string  = corrector.clean(corrector.text[self.begin:self.end]) # self.clean(corrector.text[self.begin:self.end])
                self.page    = corrector.get_pagenumber(char_begin)
                self.line    = corrector.get_linenumber(char_begin)

        if check_property_exists(tag, "HasType"):
            target = SemanticEntity({'SemanticClass':'E55 Type','string':tag["HasType"].strip()}, corrector, virtual=True)
            property = SemanticProperty({"SemanticProperty":"P2 has type"}, virtual=True, source=self, target=target)
    
    def __str__(self):
        return f"{self.type}: '{self.string}'"
        
    def __len__(self):
        return len(self.incoming)+len(self.outgoing)
    
    def verbose(self):
        return f"{self.type}: '{self.string}' ({self.id}, {self.institution} {self.year})"
    


class SemanticProperty(object):
    virtuals = []
    next_id  = 0
    PATTERN = re.compile("^(.*?) \(")
    def __init__(self, tag, entity_map=None, virtual=False, source=None, target=None, year=None, institution=None):
        self.id = self.next_id
        self.processed = False # Variable which can be used in recursion algorithms, USE WITH CAUTION
        SemanticProperty.next_id += 1
        
        self.year = year
        self.institution = institution
        
        if not check_property_exists(tag, "SemanticProperty"): self.type = "P0 Unknown"
        else:
            match = SemanticProperty.PATTERN.search(tag["SemanticProperty"].strip())
            if match: self.type = match.group(1)
            else: self.type = tag["SemanticProperty"].strip()

        
        if virtual:
            assert isinstance(source, SemanticEntity) and isinstance(target, SemanticEntity)
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
        if self.source: return f"{str(self.source):<90} → {self.type:<30} → {str(self.target):<50}"
        return f"{str(self.source_id):<90} → {str(self.type):<30} → {str(self.target_id):<50}"
    

        

def parse_postprocessing(tag_string, source, anchors, corrector):
    #print(f"Parsing post for {str(source)}")
    
    virtual_from_source = False # really no string
    for info in tag_string.split('|'):
        lowered_info = info.lower()
        if lowered_info == "virtual":
            virtual_from_source = True
            continue
        
        
        if lowered_info.startswith('!'): inverse = True
        else: inverse = False
        
        if "anchor" in lowered_info:
            if ':' in lowered_info:
                double = info.split(':')
                assert len(double) == 2
                
                anchors.properties[double[1].lower()].append((double[0],source))
            else:
                # source ist selbst ein Anchor
                assert lowered_info not in anchors.objs
                anchors.objs[lowered_info] = source
            continue
                
        else:
            triple = info.lstrip('!').split(':')
            if len(triple) != 3:
                print(triple)
            assert len(triple) == 3
        
        if inverse:
            target = SemanticEntity({'SemanticClass':triple[1],'string':f"{triple[2]}"}, corrector, virtual=True, year=source.year, institution=source.institution)
            property = SemanticProperty({"SemanticProperty":triple[0]}, virtual=True, source=target, target=source, year=source.year, institution=source.institution)
        else:
            target = SemanticEntity({'SemanticClass':triple[1],'string':triple[2]}, corrector, virtual=True, year=source.year, institution=source.institution)
            property = SemanticProperty({"SemanticProperty":triple[0]}, virtual=True, source=source, target=target, year=source.year, institution=source.institution)
        
    return virtual_from_source

def postprocessing(entities, properties):
    pass

def consolidate_properties(property, queen, incoming=True):
    assert isinstance(property, SemanticProperty) and isinstance(queen, SemanticEntity)
    if incoming:
        property.target = queen
    else:
        property.source = queen
    return property
    

def consolidate_entities(entities, entity_map):
    only_one_entity_needed = ("E55 Type", "E78 Curated Holding", "E21 Person", "E53 Place", "E28 Conceptual Object")
    uniques = defaultdict(dict)
    
    matches = 0
    for entity in entities:
        if entity.type in only_one_entity_needed and "chausammlung" not in entity.string:
            entity_string = entity.string.lower()
            if entity_string in uniques[entity.type]:
                queen = uniques[entity.type][entity_string]
                queen.incoming += [consolidate_properties(p, queen, incoming=True) for p in entity.incoming]
                queen.outgoing += [consolidate_properties(p, queen, incoming=False) for p in entity.outgoing]
                entity_map[entity.original_id] = queen
                matches += 1
                print(f"    Resolved {entity}({entity.id}) to {queen}({queen.id})")
            else:
                uniques[entity.type][entity_string] = entity
    
    result = set(entity_map.values())
    assert len(entities)-matches == len(result)
    
    print(f"{len(entities)} Entities resolved to {len(result)} Entities")
    return result, entity_map


def set_anchors(anchors):
    for anchor_str, anchor in anchors.objs.items():
        for double in anchors.properties[anchor_str]:
            if double[0].startswith('!'):
                property = SemanticProperty({"SemanticProperty":double[0].lstrip('!')}, virtual=True, source=anchor, target=double[1])
            else:
                property = SemanticProperty({"SemanticProperty":double[0]}, virtual=True, source=double[1], target=anchor)

def check_property_exists(obj, property):
    if isinstance(obj, BS4_TAG):
        return obj.has_attr(property)
    return property in obj

def parse(filepath, verbose=False, year=None, institution=None):
    '''returns (Corrected Text: string, Semantic Entities: list, Semantic Properties: list with Pointers to objects in Entities list)
    '''
    
    print(f"Parsing {filepath}:")
    with open(filepath, 'r', encoding="utf-8") as f:
        xml = BeautifulSoup(f, "xml")
    
    text = xml.find("cas:Sofa")["sofaString"]
    corrector = Corrector(xml.find_all("custom:OCRCorrection"), text)
    text = corrector.apply(text)
    if verbose: print(f"    Applied {len(corrector)} OCR-Corrections")
    
    anchors = Anchors()
    
    entities = [SemanticEntity(tag, corrector, anchors, year=year, institution=institution) for tag in xml.find_all("custom:SemanticEntities")]
    if verbose: print(f"    Parsed {len(entities)} original and {len(SemanticEntity.virtuals)} virtual Entities")
    entities += SemanticEntity.virtuals
    
    set_anchors(anchors)
    entity_map = {e.original_id:e for e in entities}
    entities, entity_map = consolidate_entities(entities, entity_map) # Types and Holdings
    
    properties = [SemanticProperty(tag, entity_map, year=year, institution=institution) for tag in xml.find_all("custom:SemanticRelations")]
    if verbose: print(f"    Parsed {len(properties)} original and {len(SemanticProperty.virtuals)} virtual Properties\n")
    properties += SemanticProperty.virtuals
    
    SemanticProperty.virtuals.clear()
    SemanticEntity.virtuals.clear()
    return text, entities, properties

def extract_ins_year(filename):
    FILENAME_PATTERN = re.compile("^(\d\d\d\d)_(.*?)_(\d?\d?\d)-(\d?\d?\d)\.xmi$")
    verbose_institutions = {
        "Museum": "Museum für Naturkunde - Allgemeine Verwaltung",
        "Geologisch-paläontologische": "Geologisch-paläontologisches Institut und geologisch­paläontologische Sammlung",
        "Mineralogisch-petrographische": "Mineralogisch-petrographisches Institut und mineralogisch-petrographische Sammlung",
        "Zoologische": "Zoologisches Institut und zoologische Sammlung"
    }
    
    match = FILENAME_PATTERN.search(filename)
    assert match
    year = int(match.group(1))
    institution = verbose_institutions[match.group(2)]
    page_begin = int(match.group(3))
    page_end = int(match.group(4))
    
    return year, institution, page_begin, page_end
    
def serialize(obj, stringify=True):
    if isinstance(obj, SemanticProperty):
        return {
        "id": str(obj.id) if stringify else obj.id,
        "type": obj.type,
        "source": str(obj.source.id) if stringify else obj.source.id,
        "target": str(obj.target.id) if stringify else obj.target.id
        }
    elif isinstance(obj, SemanticEntity):
        return {
        "id": str(obj.id) if stringify else obj.id,
        "type": obj.type,
        "virtual": obj.virtual,
        "text": obj.string.replace('\r', '').replace('\n', ' ') if stringify else obj.string,
        "begin": obj.begin,
        "end": obj.end,
        "page": obj.page,
        "line": obj.line,
        "incoming": [str(prop.id) if stringify else prop.id for prop in obj.incoming],
        "outgoing": [str(prop.id) if stringify else prop.id for prop in obj.outgoing]
        }
    else:
        return obj

def save_json(filepath, file, text, entities, properties):
    year, institution, page_begin, page_end = extract_ins_year(file)
    export = {
        "Institution": institution,
        "Year": year,
        "Page_Begin": page_begin,
        "Page_End": page_end,
        "Text": text,
        "Entities": {serialized['id']:serialized for e in entities if (serialized := serialize(e))},
        "Properties": {serialized['id']:serialized for p in properties if (serialized := serialize(p))}
    }
    assert len(export["Entities"]) == len(entities) and len(export["Properties"]) == len(properties)
    
    json_file = f"{file.rstrip('.xmi')}.json"
    with open(os.path.join(filepath, json_file), 'w', encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, indent=4)
    
    print(f"\nSaved '{file}' as JSON to '{os.path.join(filepath, json_file)}'\n")
    
def get_data_for_pickling(file, text, entities, properties):
    year, institution, page_begin, page_end = extract_ins_year(file)
    export = {
        "Institution": institution,
        "Year": year,
        "Page_Begin": page_begin,
        "Page_End": page_end,
        "Text": text,
        "Entities": {e.id:e for e in entities},
        "Properties": {p.id:p for p in properties}
    }
    assert len(export["Entities"]) == len(entities) and len(export["Properties"]) == len(properties)
    return export


def stats_directory(dirpath, save=False):
    class_counter = Counter()
    properties_counter = Counter()
    
    for_pickling = []
    
    JSON_PATH = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/JSON/"
    for file in os.listdir(dirpath):
        if file.endswith(".xmi"):
            year, institution, _, __ = extract_ins_year(file)
            text, entities, properties = parse(os.path.join(dirpath, file), year=year, institution=institution)
            class_counter.update([e.type for e in entities])
            properties_counter.update([p.type for p in properties])
            #print("\n".join([str(e) for e in properties]))
            
            if save:
                save_json(JSON_PATH, file, text, entities, properties)
                for_pickling.append(get_data_for_pickling(file, text, entities, properties))
            
            '''
            for e in entities:
                if "Condition" in e.type:
                    for i in e.incoming:
                        print(f"Incoming: {str(i)}-->{str(i.source)}")
                    for i in e.outgoing:
                        print(f"outgoing: {str(i)}-->{str(i.target)}")'''
    
    if for_pickling:
        with open("C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle", 'wb') as f:
            pickle.dump(for_pickling, f)
    
    print(f"\n\nParsed Entites in '{dirpath}':\n\n{len(class_counter)} Types with {sum(class_counter.values())} instances")
    for t, c in class_counter.most_common():
        print(f"| {t:<90} | {c:<5} |")
        
    print(f"\n\nParsed Properties in '{dirpath}':\n\n{len(properties_counter)} Types with {sum(properties_counter.values())} instances")
    for t, c in properties_counter.most_common():
        print(f"| {t:<90} | {c:<5} |")
    
    
if __name__ == "__main__":
    DIR_PATH = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/INCEpTION/UIMA_CAS_XMI"
    stats_directory(DIR_PATH, save=True)
    
    exit(3)

    TEST_FILE = "C:/Users/Aron/Downloads/webanno5422277547538360861export/1889_Zoologische_140-144.xmi"#"C:/Users/Aron/Downloads/webanno17844155560286750721export/1889_Geologisch-paläontologische_137-138.xmi"#"C:/Users/Aron/Downloads/webanno3163352340135431318export/1887_Museum_67-67.xmi"
    text, entities, properties = parse(TEST_FILE)
    print(text, '\n')
    
    print("\n".join([str(e) for e in properties]))


