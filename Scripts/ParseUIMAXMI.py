import os
from collections import defaultdict, Counter
from operator import attrgetter
from itertools import chain
import json, re
import pickle
from bs4 import BeautifulSoup
from bs4.element import Tag as BS4_TAG


class SemanticData(object):
    def __init__(self, filepath, load=True):
        if load: self.data = self.load_pickle(filepath)
        else: self.data = process_directory(filepath, save=False, consolidate=False)
        
        self.entities = list(chain.from_iterable(file["Entities"].values() for file in self.data))
        self.properties = list(chain.from_iterable(file["Properties"].values() for file in self.data))
        
    def load_pickle(self, filepath):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        return data


class Anchors(object):
    def __init__(self):
        self.objs         = {} # anchor_string:Entity
        self.properties   = defaultdict(list) #anchor_string:[(property_string, target_entity)]     


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
        self.corrections       = sorted([OCRCorrection(tag, text) for tag in tags], key=attrgetter('begin'))
        self.offsets           = {}
        self.text              = text
        self.pagenumbers       = {}
        self.linenumbers       = {}
        self.lineidx_from_orig = {0:0,}
        self.lines             = []
        self.strict_cleaner    = str.maketrans("", "", " \n\r‑-­")
        self.cleaner_for_incorrect_linebreaks = str.maketrans("­", "-", "\n\r")
        self.cleaner           = str.maketrans("", "", "\n\r­")
        
    def __len__(self):
        return len(self.corrections)
    
    def apply(self, text):
        if not self.corrections:
            self.set_pagenumbers()
            self.set_linenumbers()
            self.delete_meaningless_lines()
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
        self.delete_meaningless_lines()
        return self.text
    
    def strict_clean(self, txt):
        return txt.translate(self.strict_cleaner)
    
    def clean(self, txt):
        txt = txt.strip()
        if (soft_hyphen := txt.find('­')) > -1:
            if soft_hyphen < len(txt)-1 and txt[soft_hyphen+1].isupper():
                return txt.translate(self.cleaner_for_incorrect_linebreaks)
        return txt.translate(self.cleaner)
    
    def set_pagenumbers(self):
        BEGIN_PATTERN = re.compile(r"====PAGEBEGIN (\d+?)====\r?\n\r?\n", flags=re.MULTILINE)
        BREAK_PATTERN = re.compile(r"\r?\n\r?\n====PAGEBREAK TO (\d+?)====\r?\n\r?\n", flags=re.MULTILINE)
        begin = BEGIN_PATTERN.search(self.text)
        self.pagenumbers[begin.end()] = int(begin.group(1))
        for match in BREAK_PATTERN.finditer(self.text):
            self.pagenumbers[match.end()] = int(match.group(1))

        
    def set_linenumbers(self):
        LINEBREAK_PATTERN = re.compile('\r?\n|­')
        pages = list(self.pagenumbers) + [len(self.text)]
        
        for pagestart, pageend in zip(pages, pages[1:]):
            self.linenumbers[pagestart] = 1
            for i, match in enumerate(LINEBREAK_PATTERN.finditer(self.text[pagestart:pageend]), start=2):
                self.linenumbers[match.start()+pagestart] = i

        for i, match in enumerate(LINEBREAK_PATTERN.finditer(self.text), start=1):
            self.lineidx_from_orig[match.start()] = i
        
        self.lines = []
        cursor = 0
        for match in re.compile('\r?\n|(­)').finditer(self.text):
            if match.group(1): self.lines.append(f"{self.text[cursor:match.start()]}-")
            else: self.lines.append(self.text[cursor:match.start()])
            cursor = match.end()
        self.lines.append(self.text[cursor:len(self.text)])
        
    def delete_meaningless_lines(self):
        LINENUMBER_PATTERN = re.compile(r"\d")
        VOCALS_PATTERN = re.compile(r"[aeiouäüö]", flags=re.IGNORECASE)
        
        for i, line in enumerate(self.lines):
            if line.startswith("====P"):
                if i-2 >= 0:
                    last_line = self.lines[i-2]
                    if len(last_line)<8 and (LINENUMBER_PATTERN.search(last_line) or VOCALS_PATTERN.search(last_line) is None):
                        #print(f"    Delete last line {self.lines[i-2]}")
                        self.lines[i-2] = ""
                if i+2 < len(self.lines):
                    next_line = self.lines[i+2]
                    if len(next_line)<8 and (LINENUMBER_PATTERN.search(next_line) or VOCALS_PATTERN.search(next_line) is None):
                        #print(f"    Delete next line {self.lines[i+2]}")
                        self.lines[i+2] = ""
    
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
        
    def get_lineidx(self, index):
        cursor = index+1
        if self.lineidx_from_orig:
            while 0 <= cursor:
                if cursor in self.lineidx_from_orig: return self.lineidx_from_orig[cursor]
                cursor -= 1
        return 0
        
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
    SHORT_TYPE_PATTERN = re.compile(r"^(E\d+?) ")
    def __init__(self, tag, corrector, anchors=None, virtual=False, year=0, institution=None, virtual_origin=None):
        '''virtual_origin: source from which virtual entity gets added in Postprocessing for page and line numbers'''
        self.id = self.next_id
        self.processed = False # Variable which can be used in recursion algorithms, USE WITH CAUTION
        SemanticEntity.next_id += 1
        
        self.year = year
        self.institution = institution
        self.mentions = 1 # count of how many entities are consolidated with this one
        
        if not check_property_exists(tag, "SemanticClass"): self.type = "E0 Unknown"
        else: self.type = tag["SemanticClass"].strip()
        self.short_type = self.SHORT_TYPE_PATTERN.search(self.type).group(1)
        self.incoming = []
        self.outgoing = []
        
        if virtual:
            self.original_id   = f"V{self.id}"
            self.virtual       = True
            self.begin         = None
            self.end           = None
            self.string        = corrector.clean(tag["string"])
            self.search_string = corrector.strict_clean(self.string)
            SemanticEntity.virtuals.append(self)
            if virtual_origin and isinstance(virtual_origin, SemanticEntity):
                self.page          = virtual_origin.page
                self.line          = virtual_origin.line
                self.line_idx      = virtual_origin.line_idx
            else:
                self.page          = -1
                self.line          = -1
                self.line_idx      = 0
            
        else:
            self.original_id = int(tag["xmi:id"])
            virtual_from_source = False
            
            char_begin = int(tag["begin"])
            char_end = int(tag["end"])
            
            if tag.has_attr("Postprocessing"):
                virtual_from_source = parse_postprocessing(tag['Postprocessing'], self, anchors, corrector)
                
            if not virtual_from_source and check_property_exists(tag, "Virtual"):
                virtual_from_source = tag["Virtual"] == "true"
            
            if virtual_from_source and self.short_type not in ("E78","E21","E53","E28","E74"):
                self.virtual       = True
                self.begin         = None
                self.end           = None
                self.string        = "(implicit) Unknown"
                self.search_string = corrector.strict_clean(self.string)
                self.page          = corrector.get_pagenumber(char_begin)
                self.line          = corrector.get_linenumber(char_begin)
                self.line_idx      = corrector.get_lineidx(char_begin)
            else:
                self.virtual = False
                self.begin   = corrector.offset(char_begin)
                self.end     = corrector.offset(char_end)
                self.string  = corrector.clean(corrector.text[self.begin:self.end])
                self.search_string = corrector.strict_clean(self.string)
                self.page    = corrector.get_pagenumber(char_begin)
                self.line    = corrector.get_linenumber(char_begin)
                self.line_idx= corrector.get_lineidx(char_begin)

        if check_property_exists(tag, "HasType"):
            target = SemanticEntity({'SemanticClass':'E55 Type','string':tag["HasType"].strip()}, corrector, anchors=anchors, virtual=True, year=year, institution=institution)
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
    SHORT_TYPE_PATTERN = re.compile(r"^(P\d+?) ")
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
        self.short_type = self.SHORT_TYPE_PATTERN.search(self.type).group(1)

        
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
                assert False
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


def postprocessing(entities, properties, corrector):
    # Person and Place as part of Acquisition
    # Model: Person has P22 transferred title to (via Postprocessing Field in Inception) and has P53 location
    for e in entities:
        if e.short_type == "E21" or e.short_type == "E74": # Person or Group
            p53, p22 = [], None
            for p in e.outgoing:
                if p.short_type == "P53": p53.append(p) # Person has Place
                elif p.short_type == "P22": p22 = p # Person transferred to Collection
                
            if p53 and p22 is not None:
                
                if p22.type.endswith('E96'):
                    acquisition = SemanticEntity({'SemanticClass':'E96 Purchase','string':'(implicit) Unknown'}, corrector, virtual=True, year=e.year, institution=e.institution, virtual_origin=e)
                    p22.type = p22.type.rstrip('E96')
                elif p22.type.endswith('TRADE'):
                    acquisition = SemanticEntity({'SemanticClass':'E8 Acquisition','string':'(implicit) Unknown'}, corrector, virtual=True, year=e.year, institution=e.institution, virtual_origin=e)
                    trade = SemanticEntity({'SemanticClass':'E55 Type','string':'Trade'}, corrector, virtual=True, year=e.year, institution=e.institution)
                    SemanticProperty({"SemanticProperty":"P2 has type"}, virtual=True, source=acquisition, target=trade, year=e.year, institution=e.institution)
                    p22.type = p22.type.rstrip('TRADE')
                else:
                    acquisition = SemanticEntity({'SemanticClass':'E8 Acquisition','string':'(implicit) Unknown'}, corrector, virtual=True, year=e.year, institution=e.institution, virtual_origin=e)
                object = SemanticEntity({'SemanticClass':'E21 Physical Object','string':'(implicit) Unknown'}, corrector, virtual=True, year=e.year, institution=e.institution, virtual_origin=e)
                
                SemanticProperty({"SemanticProperty":"P23 transferred title from"}, virtual=True, source=acquisition, target=e, year=e.year, institution=e.institution)
                SemanticProperty({"SemanticProperty":"P24 transferred title of"}, virtual=True, source=acquisition, target=object, year=e.year, institution=e.institution)
                
                for p in p53: p.source = object
                p22.source = acquisition
                
                #print(f"\n\nADDED ACQUISITION FOR {e.verbose()}\n\n\n")
                
    
    # Donation Type
    donation = None
    for e in entities:
        if e.type.startswith("E8 "):
            has_type = False
            for p in e.outgoing:
                if p.type.startswith("P2 "):
                    has_type = True
                    break
            if not has_type:
                if donation is None: donation = SemanticEntity({'SemanticClass':'E55 Type','string':'Donation'}, corrector, virtual=True, year=e.year, institution=e.institution)
                SemanticProperty({"SemanticProperty":"P2 has type"}, virtual=True, source=e, target=donation, year=e.year, institution=e.institution)
    

    entities += SemanticEntity.virtuals
    properties += SemanticProperty.virtuals
    
    SemanticProperty.virtuals.clear()
    SemanticEntity.virtuals.clear()
    return entities, properties


def consolidate_property(property, queen, incoming=True):
    assert isinstance(property, SemanticProperty) and isinstance(queen, SemanticEntity)
    if incoming:
        property.target = queen
    else:
        property.source = queen
    return property
    

def consolidate_entities(entities, verbose=False):
    only_one_entity_needed = ("E55 Type", "E78 Curated Holding", "E21 Person", "E53 Place", "E28 Conceptual Object")
    uniques = defaultdict(dict)
    
    entity_map = {e.id:e for e in entities}
    assert len(entity_map) == len(entities)
    matches = 0
    for entity in entities:
        if entity.type in only_one_entity_needed and "chausammlung" not in entity.string:
            entity_string = entity.search_string
            if entity_string in uniques[entity.type]:
                queen = uniques[entity.type][entity_string]
                queen.incoming += [consolidate_property(p, queen, incoming=True) for p in entity.incoming]
                queen.outgoing += [consolidate_property(p, queen, incoming=False) for p in entity.outgoing]
                queen.mentions += 1
                entity_map[entity.id] = queen
                matches += 1
                if verbose: print(f"    Resolved {entity}({entity.id}) to {queen}({queen.id})")
            else:
                uniques[entity.type][entity_string] = entity
    
    result = set(entity_map.values())
    #assert len(entities)-matches == len(result)
    if len(entities)-matches != len(result):
        print(f"{len(entities)}-{matches} != {len(result)}")
        print('\n'.join(e.verbose() for e in set(entities).difference(result)))
        exit()
    
    if verbose: print(f"{len(entities)} Entities resolved to {len(result)} Entities")
    return result


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


def save_anchors_to_file(anchors, filepath, year, institution):
    with open(filepath, 'a', encoding="UTF-8") as f:
        f.write(f"{year}, {institution}:\n")
        for anchor_str, anchor_entity in anchors.objs.items():
            f.write(f"    {anchor_str:<9}: {anchor_entity.verbose()}\n")
        f.write('\n')


def parse(filepath, verbose=True, year=None, institution=None, consolidate=True, save_anchors=None):
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

    properties = [SemanticProperty(tag, entity_map, year=year, institution=institution) for tag in xml.find_all("custom:SemanticRelations")]
    
    if verbose: print(f"    Parsed {len(properties)} original and {len(SemanticProperty.virtuals)} virtual Properties\n")
    properties += SemanticProperty.virtuals
    
    if isinstance(save_anchors, str): save_anchors_to_file(anchors, save_anchors, year, institution)

    SemanticProperty.virtuals.clear()
    SemanticEntity.virtuals.clear()
    
    entities, properties = postprocessing(entities, properties, corrector)
    
    if consolidate: entities = consolidate_entities(entities) # Types and Holdings
    else: entities = set(entities)
    
    assert len(set(e.id for e in entities)) == len(entities)
    return text, corrector.lines, entities, properties


def extract_metadata(filename):
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
        "short_type": obj.short_type,
        "source": str(obj.source.id) if stringify else obj.source.id,
        "target": str(obj.target.id) if stringify else obj.target.id
        }
    elif isinstance(obj, SemanticEntity):
        return {
        "id": str(obj.id) if stringify else obj.id,
        "type": obj.type,
        "short_type": obj.short_type,
        "virtual": obj.virtual,
        "text": obj.string,
        "search_string": obj.search_string,
        "begin": obj.begin,
        "end": obj.end,
        "page": obj.page,
        "line": obj.line,
        "txt_id": f"{obj.institution[:3]}_{obj.year}",
        "line_idx": obj.line_idx,
        "institution": obj.institution,
        "year": obj.year,
        "mentions": obj.mentions,
        "incoming": [str(prop.id) if stringify else prop.id for prop in obj.incoming],
        "outgoing": [str(prop.id) if stringify else prop.id for prop in obj.outgoing]
        }
    else:
        return obj


def save_webdata(entities, properties, lines, filepath="../Website/src/data"):
    export_items = {
        "Entities": {serialized['id']:serialized for e in sorted(entities, key=attrgetter('year'), reverse=True) if (serialized := serialize(e))},
        "Properties": {serialized['id']:serialized for p in properties if (serialized := serialize(p))},
        "Texts": lines
    }
    #assert len(export_items["Entities"]) == len(entities) and len(export_items["Properties"]) == len(properties)
    
    with open(os.path.join(filepath, "webdata.json"), 'w', encoding="utf-8") as f:
        json.dump(export_items, f, ensure_ascii=False, indent=2)
        
    entity_classes = Counter(e["type"] for e in export_items["Entities"].values())
    property_classes = Counter(p["type"] for p in export_items["Properties"].values())
    years = Counter(e["year"] for e in export_items["Entities"].values())
    institutions = Counter(e["institution"] for e in export_items["Entities"].values())
    
    export_classes = {
        "Entities": [f"{t[0]} ({t[1]})" for t in entity_classes.most_common()],
        "Properties": [f"{t[0]} ({t[1]})" for t in property_classes.most_common()],
        "Years": [f"{t} ({years[t]})" for t in sorted(years)],
        "Institutions": [f"{t[0]} ({t[1]})" for t in institutions.most_common()]
    }
    
    with open(os.path.join(filepath, "class_stats.json"), 'w', encoding="utf-8") as f:
        json.dump(export_classes, f, ensure_ascii=False, indent=2)
    
    print(f"Saved all Entities, Properties and Class stats as JSON to '{filepath}'\n")


def save_json(filepath, file, text, entities, properties):
    year, institution, page_begin, page_end = extract_metadata(file)
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
    
    print(f"    Saved '{file}' as JSON to '{os.path.join(filepath, json_file)}'\n")


def get_data_for_pickling(file, lines, text, entities, properties):
    year, institution, page_begin, page_end = extract_metadata(file)
    export = {
        "Institution": institution,
        "Year": year,
        "Page_Begin": page_begin,
        "Page_End": page_end,
        "Text": text,
        "Lines": lines,
        "Entities": {e.id:e for e in entities},
        "Properties": {p.id:p for p in properties}
    }
    assert len(export["Entities"]) == len(entities) and len(export["Properties"]) == len(properties)
    return export


def process_directory(dirpath, save=False, consolidate=True):
    class_counter = Counter()
    properties_counter = Counter()
    
    for_pickling = []
    
    # Reset Anchors
    with open("../Data/INCEpTION/Used_Anchors.txt", 'w', encoding='UTF-8') as f:
        f.write('')
    
    JSON_PATH = "../Data/JSON/"
    for file in os.listdir(dirpath):
        if file.endswith(".xmi"):
            year, institution, _, __ = extract_metadata(file)
            
            text, lines, entities, properties = parse(os.path.join(dirpath, file), year=year, institution=institution, consolidate=consolidate, save_anchors="../Data/INCEpTION/Used_Anchors.txt")
            
            class_counter.update([e.type for e in entities])
            properties_counter.update([p.type for p in properties])
            #print("\n".join([str(e) for e in properties]))
            
            for_pickling.append(get_data_for_pickling(file, lines, text, entities, properties))
            if save:
                save_json(JSON_PATH, file, text, entities, properties)
                
    
    if save and for_pickling:
        with open("../Data/ParsedSemanticAnnotations.pickle", 'wb') as f:
            pickle.dump(for_pickling, f)
            
        print(f"Saved all Entities, Properties as Pickle to 'C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/ParsedSemanticAnnotations.pickle'")
        save_webdata(chain.from_iterable(file["Entities"].values() for file in for_pickling), chain.from_iterable(file["Properties"].values() for file in for_pickling), {f"{file['Institution'][:3]}_{file['Year']}": file["Lines"] for file in for_pickling})
    
    print(f"\n\nParsed Entites in '{dirpath}':\n\n{len(class_counter)} Types with {sum(class_counter.values())} instances")
    for t, c in class_counter.most_common():
        print(f"| {t:<90} | {c:<5} |")
        
    print(f"\n\nParsed Properties in '{dirpath}':\n\n{len(properties_counter)} Types with {sum(properties_counter.values())} instances")
    for t, c in properties_counter.most_common():
        print(f"| {t:<90} | {c:<5} |")
    
    return for_pickling


if __name__ == "__main__":
    DIR_PATH = "../Data/INCEpTION/UIMA_CAS_XMI"
    process_directory(DIR_PATH, save=True, consolidate=True)
