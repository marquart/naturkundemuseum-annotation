import os
import sys
import csv
import re
import requests
import json
from time import sleep
from random import uniform

from collections import defaultdict
from bs4 import BeautifulSoup

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        if REBUILD:
            self.log = open(f"{os.path.basename(__file__).rstrip('.py')}_Log.txt", 'w', encoding='utf-8')
        else:
            self.log = open(f"{os.path.basename(__file__).rstrip('.py')}_Log.txt", 'a', encoding='utf-8')
            self.write("\n\n-- Continue scraping: --\n")
            
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        self.terminal.flush()
        self.log.flush()
        
    def close(self):
        self.log.close()
        sys.stdout = self.terminal
        

def logprint(message, indent=0, type=''):
    if type: print(f"{type} {message}")
    else: print(f"{' '*indent}{message}")
    

def mkdir_if_not_exists(*args):
    path = os.path.join(*args)
    if not os.path.exists(path):
        os.mkdir(path)
    
def page_range(s):
    rsult = set()
    for r in s.split(','):
        if not r: continue
        rr = r.split('-')
        assert(len(rr)==2)
        
        begin, end = int(rr[0]), int(rr[1])
        if begin == end: rsult.add(begin)
        else: rsult |= set(range(begin,end+1))
    return rsult

def build_url(document_id, scan_page_id):
    return f"https://www.digi-hub.de/viewer/!fulltext/{document_id}/{scan_page_id}/"
    
def parse_document_id(url):
    url_pattern = re.compile("https://www.digi-hub.de/viewer/image/([0-9]*)/1/LOG_0003/")
    if (match := url_pattern.search(url)): return match.group(1)
    else: return None

def request_page(url, depth=0):
    sleep(uniform(2.,7.))
    response = requests.get(url, allow_redirects=False)
    if response.status_code != 200:
        
        if depth>11: raise RecursionError(f"Max recursive depth for {url}, abort!")
        if depth>10:
            logprint(f"Near max recursive depth for {url}, wait for 60 seconds")
            sleep(60)
        return request_page(url, depth=depth+1)
    return response
    
def parse_fulltext(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.find("div", {"id": "fulltext-box"}).pre
    if text: return text.text
    else: return None

def process_document(document_id, scan_page_id):
    url = build_url(document_id, scan_page_id)
    response = request_page(url)
    fulltext = parse_fulltext(response)
    return fulltext, url

### CONFIG ###
DATA_PATH = "../Data/Chronik/"
REBUILD = False

sys.stdout = Logger()

with open("../Documentation/Webseite/Bestandsliste_Berichte_Sammlungen-des-Naturkundemuseum.csv", 'r', encoding='utf-8') as f:
    data = list(csv.reader(f))
    ins = [x for x in data[0][3:] if x and x != 'Kommentar']
    ins_labels = {x:x.split(' ')[0].strip('s') for x in ins}
    scan_pages_index = (4,6,8,10)

    assert(len(ins)==len(scan_pages_index))
    
    for line in data[2:]:
        document_id = parse_document_id(line[2])
        if not document_id:
            logprint(f"Not on digi-hub: {line}\n")
            continue
        
        if '/' in line[0]: year = int(line[0].split(' / ')[0])
        else: year = int(line[0])
        
        already_processed = {} # schema= page:fulltext
        
        mkdir_if_not_exists(DATA_PATH, str(year))
        
        logprint(f"Scraping {year}:")
        for inst, index, in zip(ins, scan_pages_index):
            scanpages = sorted(page_range(line[index]))
            origpages = sorted(page_range(line[index-1]))
            assert(len(scanpages)==len(origpages))
            
            
            logprint(f"{inst}, {len(scanpages)} pages:", indent=2)
            for page,origpage in zip(scanpages,origpages):
                filename = f"{ins_labels[inst]}_{year}_Scan{page}.json"
                filepath = os.path.join(DATA_PATH, str(year), filename)
                
                if not REBUILD and os.path.exists(filepath):
                    logprint(f"page {page} already processed and saved", indent=4)
                    continue
                
                if page in already_processed:
                    fulltext, url = already_processed[page]
                else:
                    fulltext, url = process_document(document_id, page)
                    already_processed[page] = (fulltext,url)
                    
                # save processed fulltext
                result = {
                    'URL': url,
                    'Institution': inst,
                    'Year': year,
                    'Document_ID': document_id,
                    'Scanned_Page': page,
                    'Original_Page': origpage,
                    'Text': fulltext
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                
                logprint(f"saved page {page}, {len(fulltext)} characters", indent=4)
                #break
            #break
        logprint(f"Finished {year}\n")
        #break
sys.stdout.close()

# Tesseract bestes Modell für Fraktur: tesseract .\download.png download_2021-09.txt -l frak2021-09