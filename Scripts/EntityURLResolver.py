import os
import json
from collections import defaultdict

from SemanticModels import SemanticEntity, SemanticProperty, SemanticData

def build_citation(year, page, VOLUME_TABLE):
    #Chronik der Friedrich-Wilhelms-Universität zu Berlin, Vol. 4 (1891), p. 125
    if 1899 < year < 1927:
        year_range = str(year)
    else:
        year_range = f"{year}/{str(year+1)[2:]}"
    if year in VOLUME_TABLE:
        if page: return f"Chronik der Friedrich-Wilhelms-Universität zu Berlin, Vol. {VOLUME_TABLE[year]} ({year_range}), {page}."
        return f"Chronik der Friedrich-Wilhelms-Universität zu Berlin, Vol. {VOLUME_TABLE[year]} ({year_range})."
    else:
       if page: return f"Chronik der Friedrich-Wilhelms-Universität zu Berlin ({year_range}), {page}."
       return f"Chronik der Friedrich-Wilhelms-Universität zu Berlin ({year_range})."


def build_URL_table(datapath="../../Data/Chronik/", savepath=""):
    base_url = r"https://www.digi-hub.de/viewer/!image/"    
    url_resolver   = defaultdict(dict)
    original_pages = defaultdict(dict)
    for root, dirs, files in os.walk(datapath):
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(root, file), 'r', encoding="UTF-8") as f:
                    data = json.load(f)
                
                txt_id = f'{data["Institution"][:3]}_{data["Year"]}'
                page = data["Scanned_Page"]
                doc = data["Document_ID"]
                url = f"{base_url}{doc}/{page}/-/"
                url_resolver[txt_id][page] = url
                original_pages[txt_id][page] = data["Original_Page"]
                
                citation = f"Chronik der Friedrich-Wilhelms-Universität zu Berlin VOL (YEAR):PAGE"
    if savepath:
        with open(savepath, 'w', encoding='UTF-8') as f:
            export = {'URLS':url_resolver, 'ORIGINAL_PAGES': original_pages}
            json.dump(export, f, ensure_ascii=False, indent=2)
    return url_resolver, original_pages


def get_URL_for_entity(entities, filepath=""):
    if filepath:
        with open(filepath, 'r', encoding="UTF-8") as f:
            data = json.load(f)
            URL_TABLE, ORIGINAL_PAGES = data['URLS'], data['ORIGINAL_PAGES']
    else:
        URL_TABLE, ORIGINAL_PAGES = build_URL_table()
    
    VOLUME_TABLE = {year:vol for vol, year in enumerate(range(1887, 1916), start=1)}
    if entities:
        for e in entities:
            assert isinstance(e, SemanticEntity)
            if e.page and e.page > -1:
                e.url = URL_TABLE[e.txt_id][str(e.page)]
                e.original_page = ORIGINAL_PAGES[e.txt_id][str(e.page)]
                e.cite = build_citation(e.year, e.original_page, VOLUME_TABLE)
            else:
                e.url = ""
                e.original_page = 0
                e.cite = ""
        return entities
    else:
        return URL_TABLE, ORIGINAL_PAGES, VOLUME_TABLE

if __name__ == "__main__":
    URL_TABLE, ORIGINAL_PAGES = build_URL_table(savepath="../Data/URLS.json")
