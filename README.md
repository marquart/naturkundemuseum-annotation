# Naturkundemuseum-Annotation
Semantische Annotation der Jahresberichte der Institute/Sammlungen des Naturkundemuseums in der Chronik der Friedrich-Wilhelms-Universität mit [INCEpTION](https://inception-project.github.io).

## Annotation-Layers
1. **OCR**: OCR-Fehler-Korrektur in einem Kommentar-Feld
2. **SemanticEntities**: Semantische Entitäten
3. **SemanticRelationships**: Verbindungen zwischen semantischen Entitäten

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
- Wird der Acquisition kein Type gegeben wird `P2 has type:E55 Type:Donation` induziert
- Place:

    - **Herkunftsort**: `P2 has type:E55 Type:Origin` <-- falls keine Angabe wird dieser Fall induziert
    
    - Letzter bekannter Ort der zugeführten Sammlung/Objektes: `P2 has type:E55 Type:Storage`

- `Curated Holding` ist durch `P46 is composed of` mit den folgenden verbunden:
    - Präparate (z.B. "Trockenpräparate", "Wachsmodelle") sind `Physical Objects`

      ↓  `P130 shows features of`
  
    - Anatomische Begriffe sind `Biological Objects` (z.B. Gehirn, Skelellt, Leber, Fell)

      ↓ `P128 carries`
  
    - Tiere sind `Conceptual Objects` mit `P2 has type:E55 Type:Taxon`


---
### Zugänge:Bibliothek

---
### Zugänge:Instrumente

---
### Publikationen
- Autor: `P2 has type:E55 Type:Author`
- Title: `P2 has type:E55 Type:Publication`
- Verbindung: `P94 has created (was created by)`

---
### Präparationsarbeit

---
### Sammlungsorganisation

---
### Öffentlichkeit

---
### Publikum

---
### Lehre
- `E74 Group` mit `P2 has type:E55 Type:Teaching`
- verbunden mit Anzahlen durch `has number of parts` --> `Dimension`

---
### Personalia
- Jobs sind `E41 Appellation` mit `P2 has type:E55 Type:Profession`
- Akademische Titel sind `E41 Appellation` mit `P2 has type:E55 Type:Academic Title`

---
### Gebäude
- Gebäude (z.B. das Museum für Naturkunde als Gebäude) sind beschrieben als `E77 Persistent Item` mit `P2 has type:E55 Type:Building`
- Bau von Gebäuden: `E12 Production`
- Orte in Gebäuden (z.B. Erdgeschoss): `E53 Place` mit `P2 has type:E55 Type:Building`

## Fortschritt

| Jahr | Museum | Mineralogisch-Petrographisch | Geologisch-Paläontologisch | Zoologisch |
|------|--------|------------------------------|----------------------------|------------|
| 1887 |    X   |               -              |              -             |      -     |
| 1888 |    X   |               -              |              -             |      -     |
| 1889 |    X   |               X              |              X             |      X     |
| 1890 |        |                              |                            |            |
| 1891 |        |                              |                            |            |
| 1892 |        |                              |                            |            |
| 1893 |        |                              |                            |            |
| 1894 |        |                              |                            |            |
| 1895 |        |                              |                            |            |
| 1896 |        |                              |                            |            |
| 1897 |        |                              |                            |            |
| 1898 |        |                              |                            |            |
| 1899 |        |                              |                            |            |
| 1900 |        |                              |                            |            |
| 1901 |        |                              |                            |            |
| 1902 |        |                              |                            |            |
| 1903 |        |                              |                            |            |
| 1904 |        |                              |                            |            |
| 1905 |        |                              |                            |            |
| 1906 |        |                              |                            |            |
| 1907 |        |                              |                            |            |
| 1908 |        |                              |                            |            |
| 1909 |        |                              |                            |            |
| 1910 |        |                              |                            |            |
| 1911 |        |                              |                            |            |
| 1912 |        |                              |                            |            |
| 1913 |        |                              |                            |            |
| 1914 |        |                              |                            |            |
| 1915 |        |                              |                            |            |
| 1928 |        |                              |                            |            |
| 1929 |        |                              |                            |            |
| 1930 |        |                              |                            |            |
| 1931 |        |                              |                            |            |
| 1932 |        |                              |                            |            |
| 1933 |        |                              |                            |            |
| 1934 |        |                              |                            |            |
| 1935 |        |                              |                            |            |
| 1936 |        |                              |                            |            |
| 1937 |        |                              |                            |            |
| 1938 |        |                              |                            |            |


## ToDo

### Ausstehend
- Text und Bild für Webseite verfassen (deutsch und englisch)
- Web-Team kontaktieren
- Große Runde zum Vernetzen organisieren (wg. Verknüpfen von verschiedenen Datenquellen)

### Erledigt
- [Identifikation der Seiten](https://docs.google.com/spreadsheets/d/1rg0r8WQP9fFhK58a9auRFerCYfGgzt_QPgEgJ_DOjyQ/edit?usp=sharing) in den digitalisierten Chroniken, die das Museum betreffen
- Crawlen der relevanten Volltexte
- Unicode-Normalisierung und simple OCR-Korrekturen
- Themenbereiche in den Texten klassifiziert (siehe Annotation-Guide)
- Festlegen auf Ontologie für die semantische Annotation ([CIDOC CRM 7.1.1](https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html)) 
- Präsentation für Mini-Workshop vorbereitet
