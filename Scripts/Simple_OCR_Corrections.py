import os, sys
import json
import re
from random import choice
import unicodedata as uni
from pathlib import Path

import spacy
import Logger as Log

class GermanNormalizer(object):
    '''Replace false flagged Umlaute'''
    def __init__(self, corpuspath):
        self.german_corpus = self.load_german_corpus(corpuspath)
        #self.ii_words = self.str_in_german_corpus(search='ii')
        self.normalized_umlaute = self.build_umlaut_replacement_table()
        self.soft_hyphen = uni.lookup("SOFT HYPHEN")
        self.hyphens = self.get_hyphens()
    
    def load_german_corpus(self, corpuspath):
        words = []
        with open(corpuspath, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.split(' ')[0]
                words.append(word)
        return frozenset(words)
    
    def build_umlaut_replacement_table(self):
        LOOKUP = {
        'A': ['ä','Ä'],
        'U': ['ü','Ü'],
        'O': ['ö','Ö'],
        }

        FORM_LOOKUP = {'SMALL':0, 'CAPITAL':1}

        VOCAL = re.compile(" ([A,O,U]) ")
        FORM = re.compile("^LATIN (.*?) ")
        result = {}

        for i in range(192,592):
            char = chr(i)
            name = uni.name(char)
            if (match := VOCAL.search(name)):
                form = FORM.search(name)
                if not form:
                    Log.logprint(f"Form not found for {char}, {name}", topic="Initializing Umlaute")
                    continue
                result[char] = LOOKUP[match.group(1)][FORM_LOOKUP[form.group(1)]]
        return result
    
    def get_hyphens(self):
        return frozenset(uni.lookup(name) for name in (
            "HYPHEN-MINUS",
            "SOFT HYPHEN",
            "HYPHEN",
            "NON-BREAKING HYPHEN",
            "LOW LINE",
            "TILDE",
            "MACRON",
            "MODIFIER LETTER MACRON",
            "MODIFIER LETTER LOW MACRON",
            "MODIFIER LETTER MINUS SIGN",
            "SMALL TILDE",
            "HEBREW PUNCTUATION MAQAF",
            "ARABIC FULL STOP",
            "MONGOLIAN TODO SOFT HYPHEN",
            "FIGURE DASH",
            "EN DASH",
            "EM DASH",
            "HORIZONTAL BAR",
            "OVERLINE",
            "HYPHEN BULLET",
            "MINUS SIGN",
            "HORIZONTAL LINE EXTENSION",
            "STRAIGHTNESS",
            "BOX DRAWINGS LIGHT HORIZONTAL",
            "TWO-EM DASH",
            "THREE-EM DASH",
            "PARAGRAPHOS",
            "HANGUL LETTER EU",
            "HANGUL JUNGSEONG EU",
            "SMALL EM DASH",
            "SMALL HYPHEN-MINUS",
            "FULLWIDTH HYPHEN-MINUS",
            "BRAHMI PUNCTUATION LINE",
            "BRAHMI NUMBER ONE"
        ))
        
    def normalize_linebreaks(self, text):
        result = []
        concat_next_line = False
        for line in text.split('\n'):
            line = line.strip()
            if line:
                if line[-1] in self.hyphens:
                    line = line[:-1] + self.soft_hyphen #line[:len(line)-1]
                    if concat_next_line: result[-1] += line
                    else: result.append(line)
                    concat_next_line = True
                elif concat_next_line:
                    result[-1] += line
                    concat_next_line = False
                else:
                    result.append(line)
        return '\n'.join(result)
        
    def in_corpus(self, term):
        return term.lower().replace(self.soft_hyphen, '') in self.german_corpus
    
    
    def get_index_in_doc(self, index, replacement_table):
        if index in replacement_table:
            while not replacement_table[index] or replacement_table[index] == "WHITESPACE": index -= 1
        return index
    
    def not_alpha(self, doc, index):
        return len(doc[index])<2 and not doc[index].is_alpha
    
    def get_term(self, doc, index, replacement_table, replaced_term=True):
        if index in replacement_table:
            if replaced_term: return replacement_table[self.get_index_in_doc(index, replacement_table)]
            elif replacement_table[index] == "WHITESPACE": return ''
            else: return replacement_table[index]
        return doc[index].text
        
        
    def right_expand(self, doc, base, offset, replacement_table): #--> nach jedem expand right_expand komplett durchlaufen lassen
        end = base+offset
        if offset > 4 or end>len(doc)-1 or self.not_alpha(doc, end): 
            return None
        token_range = range(base, end+1)
        term = ''.join(self.get_term(doc, i, replacement_table, replaced_term=False) for i in token_range)
        print('    ', term, 'Right', offset)
        if self.in_corpus(term.replace(self.soft_hyphen, '')):
            Log.logprint(f"{doc[base:end+1]} --> {term}", indent=4, topic="Word Expansion")
            replacement_table[base] = term
            replacement_table[end] = "WHITESPACE" # end of phrase
            for i in range(base+1, end): replacement_table[i] = ''
            return replacement_table
        return self.right_expand(doc, base, offset+1, replacement_table)
        
        
    def left_expand(self, doc, base, offset, replacement_table): #--> nach jedem expand right_expand komplett durchlaufen lassen
        start = self.get_index_in_doc(base-offset, replacement_table)
        
        if offset > 3 or start<0 or self.not_alpha(doc, start): 
            return self.right_expand(doc, base, 1, replacement_table)
        token_range = range(start, base+1)
        term = ''.join(self.get_term(doc, i, replacement_table, replaced_term=False) for i in token_range)
        print('    ', term, 'Left', offset)
        if self.in_corpus(term.replace(self.soft_hyphen, '')):
            Log.logprint(f"{doc[start:base+1]} --> {term}", indent=4, topic="Word Expansion")
            replacement_table[start] = term
            replacement_table[base] = "WHITESPACE" # end of phrase
            for i in range(start+1, base): replacement_table[i] = ''
            return replacement_table
        if (right_result := self.right_expand(doc, start, offset+1, replacement_table)): return right_result
        return self.left_expand(doc, base, offset+1, replacement_table)
    
    def expand_word(self, doc, index, replacement_table):
        if (result := self.left_expand(doc, index, 1, replacement_table)): return result
        return replacement_table
        
    def check_concat(self, doc, replacement_table):
        in_corpus = self.in_corpus
        for i, token in enumerate(doc):
            term = self.get_term(doc, i, replacement_table)
            if not term.isalpha(): continue
            
            if len(term)<=4 and not in_corpus(term):
                Log.logprint(f"Expanse on {term}:", indent=4, topic="Word Expansion")
                replacement_table = self.expand_word(doc, i, replacement_table)
        
        return replacement_table
        
    def try_extended_replacement(self, term):
        VOCALS = ('i','u','o','a')
        UMLAUTE = ('ü','ö','ä')
        if 'ii' in term:
            for umlaut in UMLAUTE:
                if self.in_corpus((corrected_term := term.replace('ii', umlaut))):
                    term = corrected_term
                    break
        for vocal in VOCALS:
            for char in (vocal, vocal.upper()):
                for i in range(term.count(char)):
                    for umlaut in UMLAUTE:
                        if self.in_corpus((corrected_term := term.replace(char, umlaut if char.islower() else umlaut.upper(), i))):
                            return corrected_term
        return term
        
    def resolve_umlaute(self, doc):
        in_corpus = self.in_corpus
        replacement_table = {}
        for i, token in enumerate(doc):
            term = token.text
            #if not term.isalpha(): continue
            corrected_term = term
            for k in self.normalized_umlaute:
                if k in corrected_term: corrected_term = corrected_term.replace(k, self.normalized_umlaute[k])
            
            if not in_corpus(corrected_term):
                corrected_term = self.try_extended_replacement(corrected_term)
            
            if corrected_term != term:
                Log.logprint(f"{term} --> {corrected_term}", indent=4, topic="Umlaut Resolvement")
                replacement_table[i] = corrected_term
        replacement_table = self.check_concat(doc, replacement_table)
        return replacement_table
        
    
    def replace_words(self, doc, replacement_table): # replacement_table= {id in doc: replacement_word}
        if not replacement_table: return doc.text
        
        '''
        matcher = Matcher(nlp.vocab)
        for index in replacement_table:
            matcher.add(str(index), [[{"TEXT":doc[index].text}]])
        '''
        Log.logprint(replacement_table, indent=4, topic="\nCleaned")
        finaltext = []
        buffer_start = 0
        #for match_id, match_start, match_end in matcher(doc):
        for match in sorted(replacement_table):
            #print(match, f"'{doc[match]}'")
            if match > buffer_start:  # If we've skipped over some tokens, let's add those in (with trailing whitespace if available)
                finaltext.append(doc[buffer_start: match].text_with_ws)
            if (correct_word := replacement_table[match]):
                if correct_word == "WHITESPACE": finaltext.append(doc[match].whitespace_)
                else: 
                    finaltext.append(correct_word) # Replace token, with trailing whitespace if available
                    if match+1 not in replacement_table: finaltext.append(doc[match].whitespace_)
            buffer_start = match + 1
        if buffer_start < len(doc): finaltext.append(doc[buffer_start:].text)
        
        return ''.join(finaltext)
        
    def process_text(self, text):
        text = self.normalize_linebreaks(text)
        
        doc = nlp(text, disable=("tok2vec", "tagger", "morphologizer", "parser", "attribute_ruler", "lemmatizer", "ner"))
        replacement_table = self.resolve_umlaute(doc)
        text = self.replace_words(doc, replacement_table)
        return text
    
    
def extract_text(filepath):
    #assert isinstance(filepath, Path)
    with filepath.open(mode='r', encoding="utf-8") as f: #with open(filepath, 'r', encoding="utf-8") as f:
        data = json.load(f)
        text = data["Text"]
    return uni.normalize("NFKC", text)
    
def mkdir_if_not_exists(*args):
    path = os.path.join(*args)
    if not os.path.exists(path):
        os.mkdir(path)

def save_text(orig_path, text):
    filename = orig_path.name.replace('.json','.txt')
    dir_ = orig_path.parents[0].name
    mkdir_if_not_exists(NEW_DATA_PATH, dir_)
    filepath = Path(NEW_DATA_PATH, dir_, filename)
    
    with filepath.open(mode='w', encoding="utf-8") as f:
        f.write(text)
    

def collect_files(datapath):
    data = []
    for root,_,files in os.walk(datapath):
        for file in files:
            if file.endswith('.json'): data.append(Path(root, file))
    return data



if __name__ == "__main__":
    sys.stdout = Log.Logger(REBUILD=True)
    nlp = spacy.load("de_core_news_sm")
    Log.logprint("Loaded Language Model")

    OLD_DATA_PATH = "../Data/Chronik"
    NEW_DATA_PATH = "../Data/Texts"
    normalizer = GermanNormalizer("../Data/Script_Data/de_freq50.txt")
    #file = Path("../Data/Chronik/1911\Zoologische_1911_Scan214.json")#choice(files)

    
    
    files = collect_files(OLD_DATA_PATH)
    for file in files:
        Log.logprint(file, topic="\n\nWorking on")
        text = extract_text(file)
        new_text = normalizer.process_text(text)
        save_text(file, new_text)
        Log.logprint(f"{file}, {len(text)} chars --> {len(new_text)} chars", topic="Finished with")
        #break
        
        
    sys.stdout.close()
    '''
    text = extract_text(Path("../Data/Chronik/1903\Zoologische_1903_Scan186.json"))
    print(file)
    print(text)
    print('\n')
    new_text = normalizer.process_text(text)
    print(new_text)
    print('\n\n')
    
    s = "H all o, wie geht es dir?"
    print(s)
    b = normalizer.process_text(s)
    print(b)
    '''
