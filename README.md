# Naturkundemuseum-Annotation
Semantische Annotation der Jahresberichte der Institute/Sammlungen des Naturkundemuseums in der Chronik der Friedrich-Wilhelms-Universität mit [INCEpTION](https://inception-project.github.io).

Im Ordner `Data` sind die zu annotierenden Texte, Zwischenspeicherstände von INCEpTION und die Annotationen in zur Weiterbearbeitung geeigneten Formaten (Pickle für Python sowie JSON) zu finden. Im Ordner `Documentation` liegen hauptsächlich Dateien, die ich für die Vorstellung des Projektes verwendet habe. Im Ordner `Scripts` sind Python-Skripte, die die Expoerte von INCEpTION postprocessen oder visuell aufbereiten. Im Ordner `website` ist der Code für das Frontend der Website im Vue-Framework zu finden. 

## ToDO (until End of August)
1. Compose Docker file (with nginx)
2. Implement Triple Search instead of single search on website, explain possibilities of our data on website
3. Document our approach, explain Annotation-to-Website pipeline in this ReadMe

### Deadlines
|                     | 06.08.                                            | 13.08.               | 20.08.                                                                     | 27.08                           |
|---------------------|---------------------------------------------------|----------------------|----------------------------------------------------------------------------|---------------------------------|
| **Website**         | 1. Data<br>2. Data functions                      | Project Information  | Deployment on test server                                                  | Deployment on production server |
| **Persistent data** | Decision on format:<br>- raw RDF?<br>- N-Triples? | Wikidata-Integration | Export-Script                                                              | ---                             |
| **Documentation**   |                                                   | Website Information  | 1. Data model<br>2. Annotation (esp. shortcuts/virtual)<br>3. Website Tech | Code                            |                         |                        |

## Annotation-Layers
1. **OCR**: OCR-Fehler-Korrektur in einem Kommentar-Feld
2. **SemanticEntities**: Semantische Entitäten
3. **SemanticRelationships**: Verbindungen zwischen semantischen Entitäten

## Reproduction

1. Install [INCEpTION](https://inception-project.github.io).
2. Load latest Project file into INCEpTION `./Data/INCEpTION/Saved_Projects/`
3. Annotate in INCEpTION
4. Export Project in INCEpTION as `UIMA CAS XMI 1.1` to `./Data/INCEpTION/Saved_Projects/`
5. If you haven't installed Python and dependencies (you need to do this only once):
    1. Install [Python (3.10)](https://www.python.org/downloads/)
    2. Navigate to `./Scripts/` in your command line
    3. Install required packages (I recommend in a [virtual environment](https://docs.python.org/3/library/venv.html)) via `pip install -r requirements.txt`
6. Execute `py UnzipInceptionSavefile.py`. Your raw annotated data can now be found in `./Data/INCEpTION/UIMA_CAS_XMI/` (one UIMA XMI file per year and report)
7. Execute `py ParseUIMAXMI.py`. Your consolidated and enriched data can now be found:
    1. As JSONs in `./Data/JSON/`
    2. As one [pickled file](https://docs.python.org/3/library/pickle.html) in `./Data/ParsedSemanticAnnotations.pickle`
    3. As one JSON for the website in `./website/public/webdata.json` (and one file with statistics for the website in `./website/public/class_stats.json`)
8. In order to generate the data for the `Analyze`-Tab on Website: execute `py BuildAnalyticsWeb.py`. Three files will be written to `./Website/public/`
    1. `./Website/public/Locations.json`
    2. `./Website/public/Persons.json`
    3. `./Website/public/Collections.json`



## Annotation-Guide


### Allgemein
- **Virtuelle Entitäten**: wird mit einem Verb z.B. mehrere unabhängige Aktionen beschrieben kann ein bedeutunsloses Wort mit `virtual` im Postprocessing-Feld markiert werden, dass als virtuelle Maske für die Annotation dient
- Verfasser des jährlichen Berichts ist Person mit `P2 has type:E55 Type:Reporter`
- Geldgeber sind `E74 Group` oder `Person` mit `P2 has type:E55 Type:Sponsor`
- Wenn zwei zu verbindende Entitäten im Annotationstool zu unpraktisch zu verbinden sind:

    1. Füge einer Entität `anchor{ID}` im Postprocessing-Feld hinzu (`ID` muss durch eine im Dokument einzigartige Zahl ersetzt werden)
    
    2. Füge der anderen Entität `{PropertyType}:anchor{ID}` hinzu (Invertieren funktioniert wie beim normalen Annotiern mit `!`)
    
        z.B. `!P46 is composed of:anchor1`
        
---
### Zugänge:Objekte
- Wird der Acquisition kein Type gegeben wird `P2 has type:E55 Type:Donation` induziert ansonsten `Purchase` bei Kauf oder `P2 has type:E55 Type:Trade` bei Tausch

- Place:

    - **Herkunftsort**: `P2 has type:E55 Type:Origin` <-- falls keine Angabe wird dieser Fall induziert
    
    - Letzter bekannter Ort der zugeführten Sammlung/Objektes: `P2 has type:E55 Type:Storage`

- `Curated Holding` ist durch `P46 is composed of` mit den folgenden verbunden:
    - Präparate (z.B. "Trockenpräparate", "Wachsmodelle") sind `Physical Objects`

      ↓  `P130 shows features of`
  
    - Anatomische Begriffe sind `Biological Objects` (z.B. Gehirn, Skelellt, Leber, Fell)

      ↓ `P128 carries`
  
    - Tiere sind `Conceptual Objects` mit `P2 has type:E55 Type:Taxon`

- Schlussnummern: `E78 Curated Holding` 

      ↓ `P43 has dimension`

        `E60 Number`

      ↓ `P2 has type`                   ↓ `P4 has time-span`

        `E55 Type: 'Schlussnummer'`       `E52 Time-Span` 

    Nummern, die nur von der Art Schlussnummern sind (z.B. Holding vermehrte sich um 60 Nummern) sind einfach `E60 Number` mit `has dimension` einer Acquisition

---
### Zugänge:Bibliothek

---
### Zugänge:Instrumente
- Acquisition oder Purchase eines Physical Objects mit `P2 has type:E55 Type:Tool`

---
### Publikationen
- Autor: `P2 has type:E55 Type:Author`
- Title: `P2 has type:E55 Type:Publication`
- Verbindung: `P94 has created (was created by)`

---
### Präparationsarbeit
- Ausbesserungen an einzelnen Objekten (und nicht ganzen `Curated Holdings` --> `Curation Activity`) sind `Modification` mit `P2 has type:E55 Type:Curation Activity`, verbunden mit Person oder Group durch `P14 carried out by`, verbunden mit der `Curated Holding` die das Objekt hält mit `refers to`

---
### Sammlungsorganisation

---
### Öffentlichkeit
- Benutzung der Sammlungen durch Externe: `E7 Activity` mit `P2 has type:E55 Type:Extern Usage`
      
      ↓ `P14 carried out by` `E21 Person`
      
      ↓ `P16 used specific object` Holding oder Object
    
    

---
### Publikum
- Besuche sind `E7 Activity` mit `P2 has type:E55 Type:Visiting`

      	↓ `P14 carried out by`

- Besucher sind `E74 Group` (z.B. Schulklassen) mit `P2 has type:E55 Type:Audience`
- Besucherzahlen sind `E54 Dimension` von `E74 Group` mit Time-Spans und `P2 has type:E55 Type:Besucherzahlen`
- Öffnungszeiten sind `E3 Condition State` mit `P2 has type:E55 Type:Opening Times` und Time-Spans als Dimensions


---
### Lehre
- `E74 Group` mit `P2 has type:E55 Type:Teaching`
- verbunden mit Anzahlen durch `has number of parts` --> `Dimension`
- Vorlesungen: `E73 Information Object` mit `P2 has type:E55 Type:Lecture`, vebunden mit Person durch `P94 has created`

---
### Personalia
- Jobs sind `E41 Appellation` mit `P2 has type:E55 Type:Profession|P2 has type:E55 Type:Intern`
- Neue Jobs ohne Personen-Nennung sind `E66 Formation` mit `P2 has type:E55 Type:Profession`, ansonsten `E85 Joining` mit `P2 has type:E55 Type:Profession`, Verbindung des Joining/Leaving/Formation mit Job-Namen (Appellation) durch `P1 is identified by`
- Beförderungen sind Joining und Leaving gleichzeitig (zwei semantische Entitäten auf dem gleichen Wort)
- Falls die Herkunft/Neue Arbeisstelle benannt ist wird das Joining/Leaving mit `P146 separated from` bzw. `P144 joined with` verknüpft
- Akademische Titel sind `E41 Appellation` mit `P2 has type:E55 Type:Academic Title`
- Aufgabe im Job sind `E29 Design or Procedure` mit `P2 has type:E55 Type:Task` und durch `P14 carried out by` mit einer Person/Job verbunden

---
### Gebäude
- Gebäude (z.B. das Museum für Naturkunde als Gebäude) sind beschrieben als `E77 Persistent Item` mit `P2 has type:E55 Type:Building`
- Bau von Gebäuden: `E12 Production`
- Orte in Gebäuden (z.B. Erdgeschoss): `E53 Place` mit `P2 has type:E55 Type:Building`


