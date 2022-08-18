import re
import unicodedata as uni
import json

DATA_PATH = "../Data/"
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
            print(f"Form not found for {char}, {name}")
            continue
        result[char] = LOOKUP[match.group(1)][FORM_LOOKUP[form.group(1)]]

print(f"Found {len(result)} quasi Umlaute:\n{result}")
with open("../Documentation/Webseite/Umlaut_Replacement_Table.json", 'w', encoding='utf-8') as f:
    json.dump(result, f)
