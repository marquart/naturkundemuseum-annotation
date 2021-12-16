import os
import json

from bs4 import BeautifulSoup
from markdownify import markdownify as markdown

if __name__ == "__main__":
    Ontology_File = "../Data/INCEpTION/cidoc_crm_v7-1-1.xml" #source: https://cidoc-crm.org/html/cidoc_crm_v7.1.1.xml, doc: https://cidoc-crm.org/html/cidoc_crm_v7.1.1.htm

    with open(Ontology_File, 'r', encoding="utf-8-sig") as f:
        xml = BeautifulSoup(f, "xml")
    
    classes = xml.find('classes').findChildren('class')
    properties = xml.find('properties').findChildren('property')
    
    entities_tagset = {"name":"CIDOC CRM Entities", "description":"CIDOC CRM 7.1.1 Entities for semantic Annotations\nsource: [https://cidoc-crm.org/html/cidoc_crm_v7.1.1.xml](https://cidoc-crm.org/html/cidoc_crm_v7.1.1.xml)\ndoc: [https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html](https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html)", "language":"en", "create_tag":False, "tags": []}
    relations_tagset = {"name":"CIDOC CRM Properties", "description":"CIDOC CRM 7.1.1 Properties for semantic Annotations\nsource: [https://cidoc-crm.org/html/cidoc_crm_v7.1.1.xml](https://cidoc-crm.org/html/cidoc_crm_v7.1.1.xml)\ndoc: [https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html](https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html)", "language":"en", "create_tag":False, "tags": []}
    
    for entity in classes:
        tag = {
            "tag_name": entity.fullName.string,
            "tag_description": markdown(f"{entity.scopeNote.string}<b>Examples:</b>\n{entity.examples.string}")
        }
        entities_tagset['tags'].append(tag)
    
    
    for property in properties:
        domain = xml.find('class', {'id': property.domain['id']}).fullName.string
        range = xml.find('class', {'id': property.range['id']}).fullName.string
        if property.examples:
            tag_description = markdown(f"{domain} → {range}\n{property.scopeNote.string}<b>Examples:</b>\n{property.examples.string}", strip=('img',))
        else:
            tag_description = markdown(f"{domain} → {range}\n{property.scopeNote.string}", strip=('img',))

        tag = {
            "tag_name": property.fullName.string,
            "tag_description": tag_description
        }
        relations_tagset['tags'].append(tag)
    
    with open("../Data/INCEpTION/CIDOC_CRM_Entities.json", 'w', encoding="utf-8") as f:
        json.dump(entities_tagset, f, indent=2, ensure_ascii=False)
        print(f"Saved Tagset with {len(entities_tagset['tags'])} Entities")
        
    with open("../Data/INCEpTION/CIDOC_CRM_Properties.json", 'w', encoding="utf-8") as f:
        json.dump(relations_tagset, f, indent=2, ensure_ascii=False)
        print(f"Saved Tagset with {len(relations_tagset['tags'])} Properties")
    
