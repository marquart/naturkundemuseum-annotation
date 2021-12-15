import os
#from pathlib import Path
import re
from collections import defaultdict


def pagebreak(pageno):
    assert pageno
    return f"\n\n====PAGEBREAK TO {pageno}====\n\n"
    

if __name__ == "__main__":
    
    INS_PATTERN = re.compile("^(.*?)_")
    PAGENO_PATTERN = re.compile("Scan(\d?\d\d)\.txt$")
    
    SOURCE_PATH = "C:/Users/Aron/Documents/Naturkundemuseum/Data/Text"
    TARGET_PATH = "../Data/Texts"
    
    result = defaultdict(dict) # year --> ins --> pageno --> text
    for root,_,files in os.walk(SOURCE_PATH):
        year =  os.path.basename(root)
        assert year
        for file in files:
            if file.endswith('.txt'):
                institution = INS_PATTERN.search(file).group(1)
                pageno = int(PAGENO_PATTERN.search(file).group(1))
                
                with open(os.path.join(root, file), 'r', encoding="utf-8") as f:
                    text = f.read()
                
                if institution in result[year]: result[year][institution][pageno] = text
                else: result[year][institution] = {pageno: text}
                
    for year, institution_data in result.items():
        for ins, pagedata in institution_data.items():
            pages = sorted(pagedata)
            data = [f"====PAGEBEGIN {pages[0]}====\n\n", pagedata[pages[0]]]
            for page in pages[1:]:
                data.append(pagebreak(page))
                data.append(pagedata[page])
            filename = f"{year}_{ins}_{pages[0]}-{pages[-1]}.txt"
            with open(os.path.join(TARGET_PATH, filename), 'w', encoding="utf-8") as f:
                f.write(''.join(data))
            print(f"Saved {filename}")
        