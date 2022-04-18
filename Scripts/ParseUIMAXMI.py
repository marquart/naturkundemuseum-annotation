import os
import sys
from collections import defaultdict, Counter
from operator import attrgetter
from itertools import chain
import json, re
import pickle
from bs4 import BeautifulSoup
from bs4.element import Tag as BS4_TAG

from SemanticModels import SemanticData, Anchors, OCRCorrection, Corrector, SemanticEntity, SemanticProperty 
from GlobalConsolidate import identify_global_consolidations




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
                object = SemanticEntity({'SemanticClass':'E19 Physical Object','string':'(implicit) Unknown'}, corrector, virtual=True, year=e.year, institution=e.institution, virtual_origin=e)
                
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
    only_one_entity_needed = ("E55", "E78", "E21", "E53", "E28", "E74")
    uniques = defaultdict(dict)
    
    entity_map = {e.id:e for e in entities}
    assert len(entity_map) == len(entities)
    matches = 0
    for entity in entities:
        if entity.short_type in only_one_entity_needed and "chausammlung" not in entity.string:
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

##### SAVING #####
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


def save_webdata(entities, properties, lines, filepath="../Website/public/"):
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


def reduce_recursion(container):
    for p in container.properties:
        p.source = p.source.id
        p.target = p.target.id
    


def process_directory(dirpath, save=False, consolidate=True):
    class_counter = Counter()
    properties_counter = Counter()
    
    container = SemanticData("")
    
    # Reset Anchors
    with open("../Data/INCEpTION/Used_Anchors.txt", 'w', encoding='UTF-8') as f:
        f.write('')
    
    JSON_PATH = "../Data/JSON/"
    for file in os.listdir(dirpath):
        if file.endswith(".xmi"):
            year, institution, page_begin, page_end = extract_metadata(file)
            
            text, lines, entities, properties = parse(os.path.join(dirpath, file), year=year, institution=institution, consolidate=consolidate, save_anchors="../Data/INCEpTION/Used_Anchors.txt")
            
            class_counter.update([e.type for e in entities])
            properties_counter.update([p.type for p in properties])
            #print("\n".join([str(e) for e in properties]))
            
            prev_entities, prev_properties = len(container.entities), len(container.properties)
            container.entities += entities
            container.properties += properties
            
            container.texts.append({'Year':year, 'Institution':institution,'Page_Begin':page_begin, 'Page_End':page_end, 'Text':text, 'Lines':lines, 'Text_ID': f"{institution[:3]}_{year}"})
            assert len(container.entities) == prev_entities+len(entities) #and len(container.properties) == prev_properties+len(properties)
            
            #for_pickling.append(get_data_for_pickling(file, lines, text, entities, properties))
            if save:
                save_json(JSON_PATH, file, text, entities, properties)
                
    if consolidate:
        global_entities, global_properties = identify_global_consolidations(container.entities, Corrector((), ""))

        container.entities += global_entities
        container.properties += global_properties
        container.texts.append({'Year':0, 'Institution':'Metadata','Page_Begin':0, 'Page_End':0, 'Text':"", 'Lines':["Artificially generated global metadata",], 'Text_ID': "Met_0"})
        class_counter.update([e.type for e in global_entities])
        properties_counter.update([p.type for p in global_properties])
        
    
    if save and len(container.entities)>0:
        save_webdata(container.entities, container.properties, {t['Text_ID']:t['Lines'] for t in container.texts})
        try:
            with open("../Data/ParsedSemanticAnnotations.pickle", 'wb') as f:
                pickle.dump(container, f)
        except RecursionError:
            reduce_recursion(container)
            print("Reduced recursion depth")
            with open("../Data/ParsedSemanticAnnotations.pickle", 'wb') as f:
                pickle.dump(container, f)
                
        print(f"Saved all Entities, Properties as Pickle to '../Data/ParsedSemanticAnnotations.pickle'")

    
    print(f"\n\nParsed Entites in '{dirpath}':\n\n{len(class_counter)} Types with {sum(class_counter.values())} instances")
    for t, c in class_counter.most_common():
        print(f"| {t:<90} | {c:<5} |")
        
    print(f"\n\nParsed Properties in '{dirpath}':\n\n{len(properties_counter)} Types with {sum(properties_counter.values())} instances")
    for t, c in properties_counter.most_common():
        print(f"| {t:<90} | {c:<5} |")
    
    return container


if __name__ == "__main__":
    DIR_PATH = "../Data/INCEpTION/UIMA_CAS_XMI"
    sys.setrecursionlimit(10000)
    process_directory(DIR_PATH, save=True, consolidate=True)
