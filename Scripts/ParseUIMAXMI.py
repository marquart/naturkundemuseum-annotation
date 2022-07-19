import os
import sys
from collections import defaultdict, Counter
from operator import attrgetter
import json, re
import pickle
from bs4 import BeautifulSoup
from bs4.element import Tag as BS4_TAG

from SemanticModels import SemanticData, Anchors, OCRCorrection, Corrector, SemanticEntity, SemanticProperty 
from GlobalConsolidate import identify_global_consolidations
from EntityURLResolver import get_URL_for_entity



def modelShortcutP22(entities, properties, corrector):    # Person and Place as part of Acquisition
    # Model: Person has P22 transferred title to (via Postprocessing Field in Inception) and has P53 location
    assert len(SemanticEntity.virtuals) == 0 and len(SemanticProperty.virtuals) == 0
    for e in entities:
        if e.short_type in ("E21","E74","E39"): # Person or Group or Actor
            p53, p22, p24 = [], None, []
            for p in e.outgoing:
                if p.short_type == "P53": p53.append(p) # Person has Place
                elif p.short_type == "P22": p22 = p # Person transferred to Collection
                elif p.short_type == "P24": p24.append(p)
                
            if p22 is not None:
                if p22.type.endswith('E96'):
                    acquisition = SemanticEntity({'SemanticClass':'E96 Purchase','string':'(implicit) Purchase'}, corrector, virtual=True, year=e.year, institution=e.institution, virtual_origin=e)
                    p22.type = p22.type.rstrip('E96')
                elif p22.type.endswith('TRADE'):
                    acquisition = SemanticEntity({'SemanticClass':'E8 Acquisition','string':'(implicit) Trade'}, corrector, virtual=True, year=e.year, institution=e.institution, virtual_origin=e)
                    trade = SemanticEntity({'SemanticClass':'E55 Type','string':'Trade'}, corrector, virtual=True, year=e.year, institution=e.institution)
                    SemanticProperty({"SemanticProperty":"P2 has type"}, virtual=True, source=acquisition, target=trade, year=e.year, institution=e.institution)
                    p22.type = p22.type.rstrip('TRADE')
                else:
                    acquisition = SemanticEntity({'SemanticClass':'E8 Acquisition','string':'(implicit) Acquisition'}, corrector, virtual=True, year=e.year, institution=e.institution, virtual_origin=e)

                SemanticProperty({"SemanticProperty":"P23 transferred title from"}, virtual=True, source=acquisition, target=e, year=e.year, institution=e.institution)
                
                if p24:
                    for p in p24:
                        e.outgoing.remove(p)
                        acquisition.outgoing.append(p)
                        p.source = acquisition    
                
                elif p53:
                    artefact = SemanticEntity({'SemanticClass':'E19 Physical Object','string':'(implicit) Object'}, corrector, virtual=True, year=e.year, institution=e.institution, virtual_origin=e)
                    SemanticProperty({"SemanticProperty":"P24 transferred title of"}, virtual=True, source=acquisition, target=artefact, year=e.year, institution=e.institution)
                
                    for p in p53:
                        e.outgoing.remove(p)
                        artefact.outgoing.append(p)
                        p.source = artefact
                
                e.outgoing.remove(p22)
                acquisition.outgoing.append(p22)
                p22.source = acquisition
                
                #print(f"\n\nADDED ACQUISITION FOR {e.verbose()}\n\n\n")
    orig_entities, orig_properties = len(entities), len(properties)
    added_entities, added_properties = len(SemanticEntity.virtuals), len(SemanticProperty.virtuals)
    
    entities += SemanticEntity.virtuals
    properties += SemanticProperty.virtuals
    
    SemanticProperty.virtuals.clear()
    SemanticEntity.virtuals.clear()
    
    assert len(entities) == orig_entities+added_entities and len(properties) == orig_properties+added_properties
    return entities, properties


def postprocessing(entities, properties, corrector):
    # Person and Place as part of Acquisition
    # Model: Person has P22 transferred title to (via Postprocessing Field in Inception) and has P53 location
    assert len(SemanticEntity.virtuals) == 0 and len(SemanticProperty.virtuals) == 0
    
    entities, properties = modelShortcutP22(entities, properties, corrector)
    assert len(SemanticEntity.virtuals) == 0 and len(SemanticProperty.virtuals) == 0

    # Donation Type
    donation = None
    for e in entities:
        if e.short_type == "E8":
            has_type = False
            for p in e.outgoing:
                if p.short_type == "P2":
                    has_type = True
                    break
            if not has_type:
                if donation is None: donation = SemanticEntity({'SemanticClass':'E55 Type','string':'Gift'}, corrector, virtual=True, year=e.year, institution=e.institution)
                SemanticProperty({"SemanticProperty":"P2 has type"}, virtual=True, source=e, target=donation, year=e.year, institution=e.institution)
    
    # P128 carries --> 	P130 shows features of
    taxon = None
    for p in properties:
        if p.short_type == "P128" and p.target.short_type == "E28":
            p.short_type = "P130"
            p.type = "P130 shows features of"
            
            # add Taxon to E28 (Conceptual Object)
        if p.short_type == "P130" and p.target.short_type == "E28":
            concept = p.target
            has_type = False
            for pp in concept.outgoing:
                if pp.short_type == "P2":
                    has_type = True
                    break
            if not has_type:
                if taxon is None: taxon = SemanticEntity({'SemanticClass':'E55 Type','string':'Taxon'}, corrector, virtual=True, year=concept.year, institution=concept.institution)
                SemanticProperty({"SemanticProperty":"P2 has type"}, virtual=True, source=concept, target=taxon, year=concept.year, institution=concept.institution)
                
            

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


def split_large_acquisitions(entities, properties, corrector):
    def copy_entity(orig, corrector):
        c = SemanticEntity({'SemanticClass':orig.type,'string':orig.string}, corrector, virtual=True, year=orig.year, institution=orig.institution, virtual_origin=orig)
        c.virtual = orig.virtual
        c.begin   = orig.begin
        c.end     = orig.end
        return c
        
    def copy_properties(old, new, exclude=()):
        for pp in old.outgoing:
            if pp.short_type not in exclude:
                SemanticProperty({"SemanticProperty":pp.type}, virtual=True, source=new, target=pp.target, year=old.year, institution=old.institution)
        for pp in old.incoming:
            if pp.short_type not in exclude:
                SemanticProperty({"SemanticProperty":pp.type}, virtual=True, source=pp.source, target=new, year=old.year, institution=old.institution)
    
    def change_source(prop, old, new):
        new.outgoing.append(p)
        prop.source = new
        old.outgoing.remove(prop)
    
    assert not SemanticProperty.virtuals and not SemanticEntity.virtuals
    for e in entities:
        if e.short_type in ("E8","E96"):
            connected_givers, connected_objs = [], []
            for p in e.outgoing:
                if p.short_type == "P23": connected_givers.append(p)
                elif p.short_type == "P24": connected_objs.append(p)
            
            # Too many givers:
            if len(connected_givers) > 3 and len(connected_objs) < 2:
                if connected_objs: obj = connected_objs[0].target
                else: obj = None
                
                for p in connected_givers[1:]:
                    person = p.target
                    acquisition = copy_entity(e, corrector)
                    
                    if obj:
                        new_obj = copy_entity(obj, corrector)
                        copy_properties(obj, new_obj, exclude=("P24",))
                        SemanticProperty({"SemanticProperty":"P24 transferred title of"}, virtual=True, source=acquisition, target=new_obj, year=e.year, institution=e.institution)
                        copy_properties(e, acquisition, exclude=("P23","P24"))
                    else:
                        copy_properties(e, acquisition, exclude=("P23",))
                    
                    change_source(p, e, acquisition)
                    #print(f"    Generated {acquisition.id}:{str(acquisition)} from {e.id}:{str(e)}")

                    
            elif len(connected_givers) == 0 and len(connected_objs) == 1:
                # potential too many places
                connected_places = []
                for p in connected_objs[0].target.outgoing:
                    if p.short_type == "P53": connected_places.append(p)
                # Too many places
                if len(connected_places) > 3:
                    obj = connected_objs[0].target
                    for p in connected_places[1:]:
                        place = p.target
                        
                        new_obj = copy_entity(obj, corrector)
                        acquisition = copy_entity(e, corrector)
                        copy_properties(e, acquisition, exclude=("P24",))
                        copy_properties(obj, new_obj, exclude=("P53","P24"))      
                        SemanticProperty({"SemanticProperty":"P24 transferred title of"}, virtual=True, source=acquisition, target=new_obj, year=e.year, institution=e.institution)
                        
                        change_source(p, obj, new_obj)
                        #print(f"    Generated {new_obj.id}:{str(new_obj)} from {obj.id}:{str(obj)}")
                        
            elif len(connected_givers) == 0 and len(connected_objs) > 3:
                # too many objects
                for p in connected_objs[1:]:
                    acquisition = copy_entity(e, corrector)
                    copy_properties(e, acquisition, exclude=("P24",))
                    
                    change_source(p, e, acquisition)
    
    orig_entities, orig_properties = len(entities), len(properties)
    added_entities, added_properties = len(SemanticEntity.virtuals), len(SemanticProperty.virtuals)
    entities += SemanticEntity.virtuals
    properties += SemanticProperty.virtuals
    SemanticProperty.virtuals.clear()
    SemanticEntity.virtuals.clear()
    assert len(entities) == orig_entities+added_entities and len(properties) == orig_properties+added_properties
    return entities, properties


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
    entities, properties = split_large_acquisitions(entities, properties, corrector)
    
    if consolidate: entities = consolidate_entities(entities) # Types and Holdings
    else: entities = set(entities)
    
    assert len(set(e.id for e in entities)) == len(entities)
    return text, corrector.lines, entities, properties

def delete_property_doublettes(container):
    c = 0
    for e in container.entities:
        for p in e.outgoing:
            for pp in e.outgoing:
                if p is not pp and p.target is pp.target and p.short_type == pp.short_type and p.year == pp.year:
                    c += 1
    print(f"{c/2} PROPERTY DOUBLES")
                    
                


def check_properties_connected_with_entitites(container):
    prop_lookup = set(container.properties)
    assert len(prop_lookup) == len(container.properties)
    
    for p in container.properties:
        assert p in p.source.outgoing
        assert p in p.target.incoming
    print("==========\nSANITY CHECK: Properties are properly connected")

    for e in container.entities:
        for p in e.outgoing:
            assert p.source is e
            assert p in prop_lookup
        for p in e.incoming:
            assert p.target is e
            assert p in prop_lookup
    print("SANITY CHECK: Entities are properly connected\n==========")

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
        "original_page": obj.original_page,
        "url": obj.url,
        "citation": obj.cite,
        "line": obj.line,
        "txt_id": obj.txt_id,
        "line_idx": obj.line_idx,
        "institution": obj.institution,
        "year": obj.year,
        "mentions": obj.mentions,
        "color": obj.color,
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
    assert len(export_items["Entities"]) == len(entities) and len(export_items["Properties"]) == len(properties)
    
    with open(os.path.join(filepath, "webdata.json"), 'w', encoding="utf-8") as f:
        json.dump(export_items, f, ensure_ascii=False, indent=None)
        
    entity_classes = Counter(e["type"] for e in export_items["Entities"].values())
    property_classes = Counter(p["type"] for p in export_items["Properties"].values())
    years = Counter(e["year"] for e in export_items["Entities"].values())
    institutions = Counter(e["institution"] for e in export_items["Entities"].values())
    
    export_classes = {
        "Entities": [f"{t[0]} ({t[1]} entities)" for t in entity_classes.most_common()],
        "Properties": [f"{t[0]} ({t[1]})" for t in property_classes.most_common()],
        "Years": [f"{t} ({years[t]})" for t in sorted(years)],
        "Institutions": [f"{t[0]} ({t[1]})" for t in institutions.most_common()]
    }
    
    with open(os.path.join(filepath, "class_stats.json"), 'w', encoding="utf-8") as f:
        json.dump(export_classes, f, ensure_ascii=False, indent=None)
    
    print(f"==========\nWEB-EXPORT: Saved all Entities, Properties and Class stats as JSON to '{filepath}'\n==========")


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
            assert len(container.entities) == prev_entities+len(entities) and len(container.properties) == prev_properties+len(properties)
            
            #for_pickling.append(get_data_for_pickling(file, lines, text, entities, properties))
            if save:
                save_json(JSON_PATH, file, text, entities, properties)
    
    print(f"\n\n==========\nBefore global consolidation: parsed Entites in '{dirpath}': {len(class_counter)} Types with {sum(class_counter.values())} instances")
    print(f"Before global consolidation: parsed Properties in '{dirpath}':{len(properties_counter)} Types with {sum(properties_counter.values())} instances\n==========")
    
    if consolidate:
        global_entities, global_properties = identify_global_consolidations(container.entities, Corrector((), ""))

        container.entities += global_entities
        container.properties += global_properties
        container.texts.append({'Year':0, 'Institution':'Metadata','Page_Begin':0, 'Page_End':0, 'Text':"", 'Lines':["Artificially generated global metadata",], 'Text_ID': "Met_0"})
        class_counter.update([e.type for e in global_entities])
        properties_counter.update([p.type for p in global_properties])
        
    # URLS and original Pages:
    container.entities = get_URL_for_entity(container.entities, filepath="../Data/URLS.json")
    
    # delete double properties
    delete_property_doublettes(container)
    
    check_properties_connected_with_entitites(container)
    
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
                
        print(f"==========\nPICKLE-EXPORT:Saved all Entities, Properties as Pickle to '../Data/ParsedSemanticAnnotations.pickle'\n==========")

    
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
