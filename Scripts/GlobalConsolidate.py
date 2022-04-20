from collections import defaultdict
from SemanticModels import SemanticEntity, SemanticProperty, SemanticData, Corrector
#from ParseUIMAXMI import SemanticEntity, SemanticProperty, SemanticData, Corrector

def generalize_global_collection(e):
    # unfinished
    LOOKUP = {
        'reptilienundamphibien': 'Reptilia und Amphibia',
        'reptiliaundamphibia': 'Reptilia und Amphibia',
        'reptilien': 'Reptilia und Amphibia',
        'reptilienundamphibien': 'Reptilia und Amphibia',
        
        'säugetiere': 'Mammalia',
        'säugethiere': 'Mammalia',
        'mammalia': 'Mammalia',
        'säugetiersammlung': 'Mammalia',
        'säugethiersammlung': 'Mammalia',
        'säugethieren': 'Mammalia',
        
        'vögel': 'Aves',
        'aves': 'Aves',
        'vogeleier': 'Aves',
        'vogelsammlung': 'Aves',
        
        'pisces': 'Pisces',
        'fischeundcrustaceen': 'Pisces',
        'hauptsammlungderfische': 'Pisces',
        'fischsammlung': 'Pisces',
        'fische': 'Pisces',
        
        'spongienundprotozoen': 'Spongien, Protozoen, Coelenterata',
        'protozoen': 'Spongien, Protozoen, Coelenterata',
        'coelenteratenundspongien': 'Spongien, Protozoen, Coelenterata',
        'colenteratenundspongien': 'Spongien, Protozoen, Coelenterata',
        'colenteraten': 'Spongien, Protozoen, Coelenterata',
        'cülenteraten': 'Spongien, Protozoen, Coelenterata',
        'cölenterata': 'Spongien, Protozoen, Coelenterata',
        'cölenteraten': 'Spongien, Protozoen, Coelenterata',
        'coelenteraten': 'Spongien, Protozoen, Coelenterata',
        'coleopteren': 'Spongien, Protozoen, Coelenterata',
        'cölenteraten,spongienundprotozoen': 'Spongien, Protozoen, Coelenterata',
        'spongienundprotozoén': 'Spongien, Protozoen, Coelenterata',
        'spongiensammlung': 'Spongien, Protozoen, Coelenterata',
        
        'hymenopterenunddipterensammlung': 'Hymenopteren und Dipteren',
        'dipteren': 'Hymenopteren und Dipteren',
        
        'tunikaten,bryozoen': 'Tunikaten und Bryozoen',
        'tunikatenundbryozoen': 'Tunikaten und Bryozoen',
        'meeresbryozoen': 'Tunikaten und Bryozoen',
        'süsswasserbryozoen': 'Tunikaten und Bryozoen',
        'bryozoén': 'Tunikaten und Bryozoen',
        'bryozoen': 'Tunikaten und Bryozoen',
        'tunikaten': 'Tunikaten und Bryozoen',
        
        'myriapoden': 'Arachniden und Myriopoden',
        'myriopoden': 'Arachniden und Myriopoden',
        'arachnidenundmyriopoden': 'Arachniden und Myriopoden',
        'arachnoidea': 'Arachniden und Myriopoden',
        'arachnoiden': 'Arachniden und Myriopoden',
        'arachnoidensammlung': 'Arachniden und Myriopoden',
        'spinnensammlung': 'Arachniden und Myriopoden',
        'arachniden': 'Arachniden und Myriopoden',
        
        'orthopterenundhemipteren': 'Orthopteren und Hemipteren',
        'hemipteren': 'Orthopteren und Hemipteren',
        
        'pycnogoniden': 'Crustaceen, Pycnogoniden, Pantopoden',
        'crustaceenundpycnogoniden': 'Crustaceen, Pycnogoniden, Pantopoden',
        'korallensammlung': 'Crustaceen, Pycnogoniden, Pantopoden',
        'crustaceenundpyenogoniden': 'Crustaceen, Pycnogoniden, Pantopoden',
        'crustaceensammlung': 'Crustaceen, Pycnogoniden, Pantopoden',
        'krustenthiereundpycnogonideln': 'Crustaceen, Pycnogoniden, Pantopoden',
        'krustenthiere': 'Crustaceen, Pycnogoniden, Pantopoden',
        'crustaceenundpantopoden': 'Crustaceen, Pycnogoniden, Pantopoden',
        
        'mollusken,brachiopodenundechinodermen': 'Mollusken, Brachyopoden, Echinoderme',
        'molluskenundbrachyopoden': 'Mollusken, Brachyopoden, Echinoderme',
        'molluskenundechinodermen': 'Mollusken, Brachyopoden, Echinoderme',
        'liasbrachiopoden': 'Mollusken, Brachyopoden, Echinoderme',
        'molluskenundbrachiopoden': 'Mollusken, Brachyopoden, Echinoderme',
        'molluskensammlung': 'Mollusken, Brachyopoden, Echinoderme',
        'hauptsammlungdermollusken': 'Mollusken, Brachyopoden, Echinoderme',
        'mollusken': 'Mollusken, Brachyopoden, Echinoderme',
        'tertiärenmollusken': 'Mollusken, Brachyopoden, Echinoderme',
        
        'regenwürmer': 'Freilebende Würmer',
        'freilebendenwürmer': 'Freilebende Würmer',
        'freilebendewürmer': 'Freilebende Würmer',
        'würmer': 'Freilebende Würmer',
        
        #'polychäten':,
        
        'foraminiferen':'Foraminiferen',
        
        'entozoén': 'Entozoen',
        'entozoen': 'Entozoen',
        
        'schmetterlinge': 'Schmetterlinge',
        
        'insektensa': 'Insekten',
        'insektensammlung': 'Insekten',
        'hauptsammlungderinsekten': 'Insekten',
        
        'neuropteren': 'Neuropteren',
        
        'lepidopteren': 'Lepidopteren',
        
        'konchyliensammlung': 'Conchifera',
    }
    if e.search_string in LOOKUP: return LOOKUP[e.search_string]
    return e.search_string


def generalize_global_person(e):
    last_name = e.string.split(' ')[-1].lower()
    return last_name


def add_identifiers(entities, Appellation):
    assert isinstance(Appellation, SemanticEntity)
    return [SemanticProperty({"SemanticProperty":"P1 is identified by"}, virtual=True, source=e, target=Appellation, institution="Metadata") for e in entities]
    

def needs_global_connector(entities):
    ins, year = entities[0].institution, entities[0].year
    for e in entities[1:]:
        if e.year != year or e.institution != ins: return True
    return False


def identify_global_consolidations(entities, corrector):
    assert len(SemanticEntity.virtuals) == 0 and len(SemanticProperty.virtuals) == 0
    consolidation_possible = ("E55", "E78", "E21", "E53", "E28", "E74")
    
    global_entities = defaultdict(list)
    for e in entities:
        if e.short_type in consolidation_possible:

            if e.short_type == "E21":
                name = generalize_global_person(e)
            elif e.short_type == "E78":
                name = generalize_global_collection(e)
            else:
                name = e.search_string

            if name in global_entities:
                global_entities[name].append(e)
            else: 
                 global_entities[name] = [e]
    
    types = {}
    result = {}
    new_entities = []
    new_properties = []
    for name, entities in global_entities.items():
        if len(entities)>1 and needs_global_connector(entities):
            #year = ', '.join(sorted(set(str(e.year) for e in entities)))
            
            anchor = min(entities, key=lambda e: len(e.string))
            Appellation = SemanticEntity({"SemanticClass":"E41 Appellation", "string":anchor.string}, corrector, virtual=True, year=0, institution="Metadata", virtual_origin=None) #(self, tag, corrector, anchors=None, virtual=False, year=0, institution=None, virtual_origin=None)
            
            connectors = add_identifiers(entities, Appellation)
            
            general_type = anchor.short_type
            if general_type not in types:
                types[general_type] = SemanticEntity({"SemanticClass":"E55 Type", "string":f"Synonym for {anchor.type}"}, corrector, virtual=True, year=0, institution="Metadata", virtual_origin=None)
            type_property = SemanticProperty({"SemanticProperty":"P2 has type"}, virtual=True, source=Appellation, target=types[general_type], year=0, institution="Metadata") # (self, tag, entity_map=None, virtual=False, source=None, target=None, year=None, institution=None)
            result[name] = len(entities)
            
            new_entities.append(Appellation)
            new_properties += [type_property] + [p for p in connectors]
    
    new_entities += list(types.values())
    SemanticEntity.virtuals.clear()
    SemanticProperty.virtuals.clear()
    print(f"==========\nGLOBAL CONSOLIDATE: Connected {sum(result.values())} entities through {len(result)} global Entities\n==========")
    return new_entities , new_properties



if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    data = SemanticData(pickle_file)
    identify_consolidations(data)
    