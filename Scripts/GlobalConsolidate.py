from collections import defaultdict, deque
from SemanticModels import SemanticEntity, SemanticProperty, SemanticData, Corrector
from ParseUIMAXMI import has_outgoing_property
#from ParseUIMAXMI import SemanticEntity, SemanticProperty, SemanticData, Corrector

def generalize_global_collection(e):
    # unfinished
    LOOKUP = {
        'reptilienundamphibien': 'Reptilia und Amphibia',
        'reptiliaundamphibia': 'Reptilia und Amphibia',
        'reptilien': 'Reptilia und Amphibia',
        'reptilienundamphibien': 'Reptilia und Amphibia',
        'kriechthiere':'Reptilia und Amphibia',
        'amphibien':'Reptilia und Amphibia',
        
        'säugetiere': 'Mammalia',
        'säugethiere': 'Mammalia',
        'mammalia': 'Mammalia',
        'säugetiersammlung': 'Mammalia',
        'säugethiersammlung': 'Mammalia',
        'säugethieren': 'Mammalia',
        
        'vögel': 'Vögel',
        'aves': 'Vögel',
        'vogeleier': 'Vögel',
        'vogelsammlung': 'Vögel',
        
        'pisces': 'Fische',
        'fischeundcrustaceen': 'Fische',
        'hauptsammlungderfische': 'Fische',
        'fischsammlung': 'Fische',
        'fische': 'Fische',
        
        'spongienundprotozoen': 'Spongien, Protozoen, Coelenterata',
        'protozoen': 'Spongien, Protozoen, Coelenterata',
        'coelenteratenundspongien': 'Spongien, Protozoen, Coelenterata',
        'colenteratenundspongien': 'Spongien, Protozoen, Coelenterata',
        'colenteraten': 'Spongien, Protozoen, Coelenterata',
        'cülenteraten': 'Spongien, Protozoen, Coelenterata',
        'cölenterata': 'Spongien, Protozoen, Coelenterata',
        'cölenteraten': 'Spongien, Protozoen, Coelenterata',
        'coelenteraten': 'Spongien, Protozoen, Coelenterata',
        'coelenteratenundprotozoen':'Spongien, Protozoen, Coelenterata',
        'spongienundcoelenteraten':'Spongien, Protozoen, Coelenterata',
        'protozoa':'Spongien, Protozoen, Coelenterata',
        
        'cölenteraten,spongienundprotozoen': 'Spongien, Protozoen, Coelenterata',
        'spongien':'Spongien',
        'spongienundprotozoén': 'Spongien',
        'spongiensammlung': 'Spongien',
        'spongiae':'Spongien',

        'coleopteren': 'Coleoptera',
        'coleoptera': 'Coleoptera',
        'käfer':'Coleoptera',
        
        'hymenopteren': 'Hymenopteren',
        'hymenoptera':'Hymenopteren',
        'hymenopterenunddipterensammlung': 'Hymenopteren und Dipteren',
        'dipteren': 'Dipteren',
        
        'tunikaten,bryozoen': 'Tunikaten und Bryozoen',
        'tunikatenundbryozoen': 'Tunikaten und Bryozoen',
        'meeresbryozoen': 'Tunikaten und Bryozoen',
        'süsswasserbryozoen': 'Tunikaten und Bryozoen',
        'bryozoén': 'Tunikaten und Bryozoen',
        'bryozoen': 'Tunikaten und Bryozoen',
        'tunikaten': 'Tunikaten und Bryozoen',
        'tunicaten':'Tunikaten und Bryozoen',
        'tunicata':'Tunikaten und Bryozoen',
        'ascidiensammlung':'Tunikaten und Bryozoen',
        'bryozoa':'Tunikaten und Bryozoen',
        
        'myriapoden': 'Arachniden und Myriopoden',
        'myriopoden': 'Arachniden und Myriopoden',
        'arachnidenundmyriopoden': 'Arachniden und Myriopoden',
        'arachnoidea': 'Arachniden und Myriopoden',
        'arachnoiden': 'Arachniden und Myriopoden',
        'arachnoidensammlung': 'Arachniden und Myriopoden',
        'spinnensammlung': 'Arachniden und Myriopoden',
        'arachniden': 'Arachniden und Myriopoden',
        'spinnenthiere':'Arachniden und Myriopoden',
        
        'orthopteren':'Orthopteren',
        'orthopterenundhemipteren': 'Orthopteren und Hemipteren',
        'hemipteren': 'Hemipteren',
        'lepidoptheren,ortopterenundhemipteren':'Orthopteren und Hemipteren',
        'hemipterenundorthopteren':'Orthopteren und Hemipteren',
        'craspedoten':'Orthopteren und Hemipteren',
        
        'pycnogoniden': 'Crustaceen, Pycnogoniden, Pantopoden',
        'crustaceenundpycnogoniden': 'Crustaceen, Pycnogoniden, Pantopoden',
        'korallensammlung': 'Crustaceen, Pycnogoniden, Pantopoden',
        'crustaceenundpyenogoniden': 'Crustaceen, Pycnogoniden, Pantopoden',
        'crustaceensammlung': 'Crustaceen, Pycnogoniden, Pantopoden',
        'krustenthiereundpycnogonideln': 'Crustaceen, Pycnogoniden, Pantopoden',
        'krustenthiere': 'Crustaceen, Pycnogoniden, Pantopoden',
        'crustaceenundpantopoden': 'Crustaceen, Pycnogoniden, Pantopoden',
        'crustaceen':'Crustaceen, Pycnogoniden, Pantopoden',
        'krebssammlung':'Crustaceen, Pycnogoniden, Pantopoden',
        'crustacea':'Crustaceen, Pycnogoniden, Pantopoden',
        
        'mollusken,brachiopodenundechinodermen': 'Mollusken, Brachyopoden, Echinoderme',
        'molluskenundbrachyopoden': 'Mollusken, Brachyopoden, Echinoderme',
        'molluskenundechinodermen': 'Mollusken, Brachyopoden, Echinoderme',
        'liasbrachiopoden': 'Mollusken, Brachyopoden, Echinoderme',
        'molluskenundbrachiopoden': 'Mollusken, Brachyopoden, Echinoderme',
        'molluskensammlung': 'Mollusken, Brachyopoden, Echinoderme',
        'hauptsammlungdermollusken': 'Mollusken, Brachyopoden, Echinoderme',
        'mollusken': 'Mollusken, Brachyopoden, Echinoderme',
        'tertiärenmollusken': 'Mollusken, Brachyopoden, Echinoderme',
        'cephalopoden':'Mollusken, Brachyopoden, Echinoderme',
        'echinodermen':'Mollusken, Brachyopoden, Echinoderme',
        'echinodermata':'Mollusken, Brachyopoden, Echinoderme',
        'brachiopoden':'Mollusken, Brachyopoden, Echinoderme',
        'mollusca':'Mollusken, Brachyopoden, Echinoderme',
        'echinodermena':'Mollusken, Brachyopoden, Echinoderme',
        
        'regenwürmer': 'Freilebende Würmer',
        'freilebendenwürmer': 'Freilebende Würmer',
        'freilebendewürmer': 'Freilebende Würmer',
        'würmer': 'Freilebende Würmer',
        'vermes':'Freilebende Würmer',
        
        #'polychäten':,
        
        'foraminiferen':'Foraminiferen',
        
        'entozoén': 'Entozoen',
        'entozoen': 'Entozoen',
        
        'schmetterlinge': 'Schmetterlinge',
        'schmetterlingssammlung':'Schmetterlinge',
        
        'insektensa': 'Insekten',
        'insekten':'Insekten',
        'insektensammlung': 'Insekten',
        'hauptsammlungderinsekten': 'Insekten',
        'ichthyologischeobjekte':'Insekten',

        'rhynchoten':'Hemipteren',
        
        'neuropteren': 'Neuropteren',
        'neuroptera':'Neuropteren',
        'neuropterenundtrichopteren':'Neuropteren',
        
        'lepidopteren': 'Lepidopteren',
        
        'konchyliensammlung': 'Conchifera',
        "paetel'schenkonchylien":'Conchifera',
        'conchifera':'Conchifera',

        'gastropoden':'Gastropoden',
        'jurassischengastropoden':'Gastropoden',
        'coniden':'Gastropoden',

        'arthropoden':'Arthropoden',
        'cirripedien':'Arthropoden',

        'odonaten':'Odonaten',

        'puliciden,pediculidenundmallophagen':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'puliciden':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'pediculiden':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'mallophagenundläuse':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'mallophagen,pediculiden,pulicidenoderpsociden':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'puliciden,mallophagenundandereparasiten':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'sammlungenderpsociden,mallophagen,pediculidenundpuliciden':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'abteilungendermallophagen,pedieuliden,pulieiden,copeognathenundgallen':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'sammlungvonpsociden,mallophagen,pediculidenundpuliciden':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'termiten,ephemeriden,psocidenoderandereniedereinsekten':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'abteilungderniedereninsekten':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'abteilungendermallophagen,pedieuliden,pulieiden,copeognathenundgallen':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',
        'gallen':'Puliciden, Pediculiden, Mallophagen, Termiten, Ephemeriden, Psociden, niedere Insekten',

        'cnidaria':'Cnidaria',
        'medusen':'Cnidaria',
        'korallen':'Cnidaria',
        'hydromedusen':'Cnidaria',
    }
    if e.search_string in LOOKUP: return LOOKUP[e.search_string]
    return e.search_string

def add_concept_to_objects(entities, properties, corrector):
    i = 0
    new_entities   = []
    new_properties = []
    for e in entities:
        if e.short_type in ("E19","E18","E20","E78","E35"):
            concept, relation = add_concept_to_object(e, corrector)
            if concept:
                assert relation is not None
                new_entities.append(concept)
                new_properties.append(relation)
                i += 1
    print(f"==========\LOCAL CONSOLIDATE: Added {i} taxonomic concepts to objects and collections\n==========")
    assert len(new_entities)==len(SemanticEntity.virtuals) and len(new_properties)==len(SemanticProperty.virtuals)
    entities += new_entities
    properties += new_properties
    
    SemanticProperty.virtuals.clear()
    SemanticEntity.virtuals.clear()
    return entities, properties

def add_concept_to_object(e, corrector):
    ''' Takes an Object (E18, E19, E20) or Title (E35) and adds P130 or P129 to a Conceptual Object based on next Holding
    '''
    # Check if Concept already exists
    #if "E28" in set(r.target.short_type for r in e.outgoing): return None, None

    # Find next Concept or Collection
    i = 0
    stack = deque([e])
    collection = None

    while stack and i < 100:
        cursor = stack.popleft()
        if cursor.short_type == "E78":
            collection = cursor
            break
        stack += [r.target for r in cursor.outgoing]
        stack += [r.source for r in cursor.incoming]
        i += 1
    if collection:
        concept_name = generalize_global_collection(collection)
        if concept_name == collection.search_string:
            print(f"CANT RESOLVE CONCEPT BASED ON COLLECTION {collection} ({collection.search_string})")
        else:
            if (target := has_outgoing_property(collection, "P130")): concept = target
            else: concept = SemanticEntity({"SemanticClass":"E28 Conceptual Object", "string":concept_name}, corrector, virtual=True, year=e.year, institution=e.institution, virtual_origin=None)
            if e.short_type == "E35":
                relation = SemanticProperty({"SemanticProperty":"P129 is about"}, virtual=True, source=e, target=concept, institution=e.institution)
            else:
                relation = SemanticProperty({"SemanticProperty":"P130 shows features of"}, virtual=True, source=e, target=concept, institution=e.institution)
            return concept, relation
    return None, None



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

    i = 0
    new_entities = []
    new_properties = []

    consolidation_possible = ("E55", "E78", "E21", "E53", "E28", "E74", "E39")
    global_entities = defaultdict(dict)
    for e in entities:
        if e.short_type in consolidation_possible:

            if e.short_type == "E21":
                name = generalize_global_person(e)
            elif e.short_type == "E78":
                name = generalize_global_collection(e)
            else:
                name = e.search_string

            if name in global_entities[e.short_type]:
                global_entities[e.short_type][name].append(e)
            else: 
                 global_entities[e.short_type][name] = [e]
    
    types = {}
    result = {}

    for name_entities in global_entities.values():
        for name, entities in name_entities.items():
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
    