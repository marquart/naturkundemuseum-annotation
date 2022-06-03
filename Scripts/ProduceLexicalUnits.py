# Basic Text-Preprocessing to lemmatize in order to produce search strings
# \Documents\WiSe_2021\DH\venv-preprocessing\

import os
import json
import spacy

from SemanticModels import Corrector

class Lemmatizer(object):
    def __init__(self):
        self.nlp = spacy.load("de_dep_news_trf")#spacy.load("de_core_news_sm", disable=("ner",))
    
    def buildLemmatizedSpan(self, text, entity):
        begin, end = entity["begin"], entity["end"]
        
        sentence, sentence_start = self.getPrimitiveSentence(text, begin, end)
        doc = self.nlp(sentence)
        firstToken = self.getTokenAtOriginalID(doc, begin-sentence_start)
        lastToken = self.getTokenAtOriginalID(doc, end-sentence_start-1)
        return ''.join(doc[i].lemma_+doc[i].whitespace_ for i in range(firstToken.i, lastToken.i+1) )
        #return ''.join(doc[i].lemma_+doc[i].whitespace_ if doc[i].pos_.startswith('A') else doc[i].text_with_ws for i in range(firstToken.i, lastToken.i+1) )
    
    def getPrimitiveSentence(self, txt, begin, end):
        start, finish = begin, end+1
        while start>0 and start<len(txt) and txt[start] not in ('.','!','?'):
            start -= 1
        while finish>0 and finish<len(txt) and txt[finish] not in ('.','!','?'):
            finish += 1
        return txt[start:finish], start


    def getTokenAtOriginalID(self, doc, char_idx):
        if char_idx == len(doc.text): return doc[-1]
        for i, token in enumerate(doc):
            if char_idx > token.idx:
                continue
            elif char_idx == token.idx:
                return token
            elif char_idx < token.idx:
                return doc[i-1]
        print(doc,char_idx, len(doc.text))
        return doc[-1]


if __name__ == "__main__":
    JSON_PATH = "../Data/JSON/"
    lemmatizer = Lemmatizer()
    corrector = Corrector([],"")
    
    table = {} #search_string:(lexical_unit, new search_string)
    for file in os.listdir(JSON_PATH):
        if file.endswith(".json"):
            with open(os.path.join(JSON_PATH, file), 'r', encoding="UTF-8") as f:
                data = json.load(f)
            text = data["Text"]
            for entity in data["Entities"].values():
                if not entity["virtual"] and entity["short_type"]=="E53":
                    lemma = corrector.clean(lemmatizer.buildLemmatizedSpan(text, entity))
                    if lemma != entity["text"] and len(lemma)<=len(entity["text"]):#and len(lemma)<len(entity["text"])
                        print(f"{entity['text']:<100} --> {lemma:<100}")
                        table[entity['search_string']] = (lemma, corrector.strict_clean(lemma).lower())
    with open("../Data/Lexical_Locations.json", 'w', encoding="UTF-8") as f:
        json.dump(table, f)
    print("Wrote output to ./Data/Lexical_Locations.json")
