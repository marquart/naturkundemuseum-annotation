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

## Fortschritt

`(X)` = Acquisitions und Schlussnummern
`(y)` = Acquisitions der Säugetiere, Vögel und Reptilien & Amphibien
`(x)` = Acquisitions der Säugetiere


| Jahr | Museum | Mineralogisch-Petrographisch | Geologisch-Paläontologisch | Zoologisch   |
|------|--------|------------------------------|----------------------------|--------------|
| 1887 |    X   |               -              |              -             |      -       |
| 1888 |    X   |               -              |              -             |      -       |
| 1889 |    X   |               X              |              X             |      X       |
| 1890 |    X   |               X              |              X             |      X       |
| 1891 |    X   |               X              |              X             |      X       |
| 1892 |        |                              |                            |      (X)     |
| 1893 |        |                              |                            |      (X)     |
| 1894 |        |                              |                            |      (X)     |
| 1895 |        |                              |                            |      (X)     |
| 1896 |        |                              |                            |      (y)     |
| 1897 |        |                              |                            |      (y)     |
| 1898 |        |                              |                            |      (y)     |
| 1899 |        |                              |                            |      (x)     |
| 1900 |        |                              |                            |      (x)     |
| 1901 |        |                              |                            |      (x)     |
| 1902 |        |                              |                            |      (x)     |
| 1903 |        |                              |                            |      (x)     |
| 1904 |        |                              |                            |      (x)     |
| 1905 |        |                              |                            |      (x)     |
| 1906 |        |                              |                            |      (x)     |
| 1907 |        |                              |                            |      (x)     |
| 1908 |        |                              |                            |      (x)     |
| 1909 |        |                              |                            |      (x)     |
| 1910 |        |                              |                            |      (x)     |
| 1911 |        |                              |                            |      (x)     |
| 1912 |        |                              |                            |      (x)     |
| 1913 |        |                              |                            |      (X)     | ausf. in Mitteilungen des Zool. Museums
| 1914 |        |                              |                            |      (X)     | ausf. in Mitteilungen des Zool. Museums
| 1915 |        |                              |                            |      (X)     | ausf. in Mitteilungen des Zool. Museums
| 1928 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums
| 1929 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums
| 1930 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums
| 1931 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums
| 1932 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums
| 1933 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums
| 1934 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums
| 1935 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums
| 1936 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums
| 1937 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums
| 1938 |        |                              |                            |              | ausf. in Mitteilungen des Zool. Museums


## ToDo

### Ausstehend
- Text und Bild für Webseite verfassen (deutsch und englisch)
- Web-Team kontaktieren
- Große Runde zum Vernetzen organisieren (wg. Verknüpfen von verschiedenen Datenquellen)
- Terminvorschlag Projektvorstellung SDI
- Franziska Schuster bzgl. SHK anschreiben

### Erledigt
- [Identifikation der Seiten](https://docs.google.com/spreadsheets/d/1rg0r8WQP9fFhK58a9auRFerCYfGgzt_QPgEgJ_DOjyQ/edit?usp=sharing) in den digitalisierten Chroniken, die das Museum betreffen
- Crawlen der relevanten Volltexte
- Unicode-Normalisierung und simple OCR-Korrekturen
- Themenbereiche in den Texten klassifiziert (siehe Annotation-Guide)
- Festlegen auf Ontologie für die semantische Annotation ([CIDOC CRM 7.1.1](https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html)) 
- Präsentation für Mini-Workshop vorbereitet
