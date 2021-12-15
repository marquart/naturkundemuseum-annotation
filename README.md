# Naturkundemuseum-Annotation
Semantische Annotation der Jahresberichte der Institute/Sammlungen des Naturkundemuseums in der Chronik der Friedrich-Wilhelms-Universität mit [INCEpTION](https://inception-project.github.io).

## Annotation-Layers
1. **OCR**: OCR-Fehler-Korrektur in einem Kommentar-Feld
2. **SemanticEntities**: Semantische Entitäten
3. **SemanticRelationships**: Verbindungen zwischen semantischen Entitäten

## Annotations-Guide


### Allgemein

1. `→` Klasse ist Source der Property (**Class → Companion**)
2. `←` Klasse ist Target der Property (**Companion → Class**)

**E21 Person**

**E53 Place**

| Type | Property | Companion | Scope |
| ---- | -------- | ------ | ----- |
| ← | P4 has time-span | \* | einzige valide Property |

**E42 Identifier**

Wikidata-ID → Postprocessing

**E52 Time-Span**

Jahr (als Integer) oder Datum, meist im Postprocessing durch Jahr des Jahresberichtes angereichert
| Type | Property | Companion | Scope |
| ---- | -------- | ------ | ----- |
| ← | P4 has time-span | \* | einzige valide Property |

**E60 Number**

Anzahl an Objekten

**E8 Acquisition**

Eigentums-Übergänge, Art (Geschenk, Kauf etc.) wird im Postprocessing durch `P2 has type` angegeben 

**E78 Curated Holding**

Sammlungen

**E20 Biological Object**

Ausstellungs-Objekte aus der Natur
| Type | Property | Companion | Scope |
| ---- | -------- | ------ | ----- |
| → | P27 moved from | E53 Place | Herkunftsort des Objektes |

**E28 Conceptual Object**

Taxonomien

**E55 Type**

| Type | Property | Companion | Scope |
| ---- | -------- | ------ | ----- |
| ← | P2 has type | \* | einzige valide Property |




---
### Zugänge:Objekte



---
### Zugänge:Bibliothek

---
### Zugänge:Instrumente

---
### Publikationen

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

---
### Personalia

---
### Gebäude


