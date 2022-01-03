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


