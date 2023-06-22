import os
from collections import defaultdict, Counter
from operator import attrgetter
import re
import pickle
import itertools

from bs4 import BeautifulSoup
from bs4.element import Tag as BS4_TAG

class SemanticData(object):
    def __init__(self, filepath, load=True):
        if filepath:
            if load: self.data = self.load_pickle(filepath)
            else: self.data = process_directory(filepath, save=False, consolidate=False)
            
            self.entities = self.data.entities
            self.properties = self.data.properties
            self.texts = self.data.texts
        else:
            self.entities = []
            self.properties = []
            self.texts = []
        
    def load_pickle(self, filepath):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        if not isinstance(data.properties[0].source, SemanticEntity):
            data = self.populate_properties(data)
        return data
    
    def populate_properties(self, data):
        entity_map = {e.id:e for e in data.entities}
        assert len(entity_map) == len(data.entities)
        for p in data.properties:
            p.source = entity_map[p.source]
            p.target = entity_map[p.target]
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
        self.pages             = {} #Pageno:text
        self.linenumbers       = {}
        self.lineidx_from_orig = {0:0,}
        self.lines             = []
        self.strict_cleaner    = str.maketrans("", "", " \n\r‑-­")
        self.cleaner_for_incorrect_linebreaks = str.maketrans("­", "-", "\n\r")
        self.cleaner_for_correct_linebreaks = str.maketrans("", "", "\n\r­")
        self.cleaner           = str.maketrans("\n", " ", "\r­")
        
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
            else:
                return txt.translate(self.cleaner_for_correct_linebreaks)
        return txt.translate(self.cleaner)
    
    def set_pagenumbers(self):
        BEGIN_PATTERN = re.compile(r"====PAGEBEGIN (\d+?)====\r?\n\r?\n", flags=re.MULTILINE)
        BREAK_PATTERN = re.compile(r"\r?\n\r?\n====PAGEBREAK TO (\d+?)====\r?\n\r?\n", flags=re.MULTILINE)
        begin = BEGIN_PATTERN.search(self.text)
        self.pagenumbers[begin.end()] = int(begin.group(1))

        pageBreakMatches = [begin]
        for match in BREAK_PATTERN.finditer(self.text):
            self.pagenumbers[match.end()] = int(match.group(1))
            pageBreakMatches.append(match)

        for start, end in zip(pageBreakMatches, pageBreakMatches[1:]):
            self.pages[self.pagenumbers[start.end()]] = self.text[start.end():end.start()]
        last_page = pageBreakMatches[-1].end()
        self.pages[self.pagenumbers[last_page]] = self.text[last_page:]

        
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
    IDs = itertools.count()
    SHORT_TYPE_PATTERN = re.compile(r"^(E\d+?) ")
    COLORS = {'E41': '#debb9baa', 'E63': '#50c4c2aa', 'E74': '#3b95c4aa', 'E21': '#3b95c4aa', 'E52': '#50c4c2aa', 'E55': '#06b67eaa', 'E85': '#fc3915aa', 'E28': '#06b67eaa', 'E19': '#5a50c4aa', 'E87': '#fc3915aa', 'E78': '#b560d4aa', 'E8': '#fc3915aa', 'E53': '#fc7715aa', 'E39': '#3b95c4aa', 'E54': '#50c4c2aa', 'E20': '#5a50c4aa', 'E35': '#debb9baa', 'E77': '#b560d4aa', 'E9': '#fc3915aa', 'E12': '#fc3915aa', 'E60': '#debb9baa', 'E7': '#fc3915aa', 'E96': '#fc3915aa', 'E86': '#fc3915aa', 'E57': '#5a50c4aa', 'E3': '#50c4c2aa', 'E66': '#fc3915aa', 'E29': '#debb9baa', 'E73': '#debb9baa', 'E11': '#fc3915aa', 'E14': '#fc3915aa', 'E79': '#fc3915aa'}
    def __init__(self, tag, corrector, anchors=None, virtual=False, year=0, institution=None, virtual_origin=None):
        '''virtual_origin: source from which virtual entity gets added in Postprocessing for page and line numbers'''
        self.id = next(SemanticEntity.IDs)
        self.processed = False # Variable which can be used in recursion algorithms, USE WITH CAUTION
        
        self.year = year
        self.institution = institution
        self.txt_id = f"{self.institution[:3]}_{self.year}"
        self.mentions = 1 # count of how many entities are consolidated with this one
        
        # gets filled in get_URL_for_entity
        self.original_page = 0 # not scanned page but pagination in document
        self.url = "" # url to digi-hub
        
        if not check_property_exists(tag, "SemanticClass"): self.type = "E0 Unknown"
        else: self.type = tag["SemanticClass"].strip()
        
        self.short_type = self.SHORT_TYPE_PATTERN.search(self.type).group(1)
        self.long_type = self.type.lstrip(self.short_type).lstrip(' ')
        
        self.color = self.get_color()
        
        self.cite = ""
        
        self.incoming = []
        self.outgoing = []
        
        if virtual:
            self.original_id   = f"V{self.id}"
            self.virtual       = True
            self.begin         = None
            self.end           = None
            self.string        = corrector.clean(tag["string"])
            self.search_string = corrector.strict_clean(self.string).lower()
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

            char_begin = int(tag["begin"])
            char_end = int(tag["end"])
            virtual_from_source = char_begin == char_end # Zero-Span Annotation, normally False
            
            if tag.has_attr("Postprocessing"):
                virtual_from_source = parse_postprocessing(tag['Postprocessing'], self, anchors, corrector)
                
            if not virtual_from_source and check_property_exists(tag, "Virtual"):
                virtual_from_source = tag["Virtual"] == "true"
            
            if virtual_from_source and self.short_type not in ("E78","E21","E53","E28","E74"):
                self.virtual       = True
                self.begin         = None
                self.end           = None
                self.string        = f"(implicit) {self.long_type}"
                self.search_string = corrector.strict_clean(self.string).lower()
                self.page          = corrector.get_pagenumber(char_begin)
                self.line          = corrector.get_linenumber(char_begin)
                self.line_idx      = corrector.get_lineidx(char_begin)
            else:
                self.virtual = False
                self.begin   = corrector.offset(char_begin)
                self.end     = corrector.offset(char_end)
                self.string  = corrector.clean(corrector.text[self.begin:self.end])
                self.search_string = corrector.strict_clean(self.string).lower()
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
        
    def get_color(self):
        if self.short_type in SemanticEntity.COLORS: return SemanticEntity.COLORS[self.short_type]
        else: return "#d3d3d3aa"
    
    def verbose(self):
        return f"{self.type}: '{self.string}' ({self.id}, {self.institution} {self.year})"
        


class SemanticProperty(object):
    virtuals = []
    IDs = itertools.count()
    PATTERN = re.compile("^(.*?) \(")
    SHORT_TYPE_PATTERN = re.compile(r"^(P\d+?) ")
    def __init__(self, tag, entity_map=None, virtual=False, source=None, target=None, year=0, institution=None):
        self.id = next(SemanticProperty.IDs)
        self.processed = False # Variable which can be used in recursion algorithms, USE WITH CAUTION
        
        
        self.year = year
        self.institution = institution
        
        if not check_property_exists(tag, "SemanticProperty"): self.type = "P0 Unknown"
        else:
            match = SemanticProperty.PATTERN.search(tag["SemanticProperty"].strip())
            if match: self.type = match.group(1)
            else: self.type = tag["SemanticProperty"].strip()
        self.short_type = self.SHORT_TYPE_PATTERN.search(self.type).group(1)
        self.long_type = self.type.lstrip(self.short_type).lstrip(' ')
        
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


def check_property_exists(obj, property):
    if isinstance(obj, BS4_TAG):
        return obj.has_attr(property)
    return property in obj


def parse_postprocessing(tag_string, source, anchors, corrector):
    #print(f"Parsing post for {str(source)}")
    
    virtual_from_source = False # really no string
    for info in tag_string.split('|'):
        lowered_info = info.lower()
        if lowered_info == "virtual":
            virtual_from_source = True
            continue
        
        inverse = lowered_info.startswith('!')

        if "anchor" in lowered_info:
            if ':' in lowered_info:
                double = info.split(':')
                assert len(double) == 2
                
                anchors.properties[double[1].lower()].append((double[0],source))
            else:
                # source ist selbst ein Anchor
                if lowered_info in anchors.objs:
                    print(lowered_info, source.original_id, source.short_type, anchors.objs)
                assert lowered_info not in anchors.objs
                anchors.objs[lowered_info] = source
            continue
                
        else:
            triple = info.lstrip('!').split(':')
            assert len(triple) == 3
            
        target = SemanticEntity({'SemanticClass':triple[1],'string':triple[2]}, corrector, virtual=True, year=source.year, institution=source.institution)
        if inverse:
            property = SemanticProperty({"SemanticProperty":triple[0]}, virtual=True, source=target, target=source, year=source.year, institution=source.institution)
        else:
            property = SemanticProperty({"SemanticProperty":triple[0]}, virtual=True, source=source, target=target, year=source.year, institution=source.institution)
        
    return virtual_from_source
