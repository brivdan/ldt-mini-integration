# Mini LDT2 / LDT3 Integration Lab

An educational Python project for a German medical-lab integration interview.

> **Important:** These samples are **synthetic partial examples**, not valid complete LDT2/LDT3 files for production exchange or KBV conformance testing. They omit required headers/footers, required fields, object attributes, complete nesting, version-specific validation, encoding negotiation, and patient-data safeguards. Some LDT3 object relationships have deliberately been flattened for teaching. Do **not** send them to real practice or laboratory software.

## Run (Python 3.10+, no dependencies)

```bash
python create_samples.py
python ldt_demo.py ldt2 samples/ldt2_demo.ldt
python ldt_demo.py ldt3 samples/ldt3_demo.ldt
python -m unittest discover -s tests -v
```

Both inputs map to the same internal JSON representation. This is a real architectural idea: **different adapters → common data model → downstream integration**.

## Look inside the files

Each line follows the xDT-style frame `LLLFFFFVALUE\r\n`:
- `LLL`: decimal byte length of the entire line, including `\r\n`
- `FFFF`: 4-digit Feldkennung (field ID)
- `VALUE`: field value

E.g. `01380008205\r\n` = length 13, `8000` (record type), `8205` (lab report).

Fields used here:

| Field | Meaning |
|---|---|
| 8000 | Satzart (record type) |
| 3101 / 3102 / 3103 | family name / given name / date of birth |
| 8410 / 8411 | test identifier / test label |
| 8420 / 8421 | result value / unit |
| 8002 / 8003 | LDT3 object begin / end |

The LDT3 example uses `Obj_0047` (person/patient) and `Obj_0060` (clinical chemistry result). Full LDT3 requires more structure and attributes than this small demonstration.

## Exercises

1. Run both adapters, compare their JSON outputs.
2. Change `8420` to `120` in `create_samples.py`, regenerate, rerun.
3. Introduce a broken length prefix and observe the failure.
4. Remove an `8003` closing marker and observe object validation.
5. Extend the common model with reference ranges, sample IDs, order IDs, multiple tests, and error reports.
6. Discuss how a proper implementation would validate a message against KBV schemas and local trading-partner agreements.

## Interview talking point (German)

> Ich würde LDT2 und LDT3 mit separaten Adaptern einlesen, zuerst die syntaktische Struktur und danach die fachlichen Pflichtfelder validieren, die Informationen in ein gemeinsames Datenmodell überführen und erst anschließend in das Zielformat mappen. Bei LDT3 müssen zusätzlich Objekthierarchien und Regeln beachtet werden. Außerdem wären Testdaten, Fehlermeldungen und die Zuordnung von Patienten, Aufträgen und Befunden wichtig.

## Authoritative references

- [KBV LDT3 3.2.19 use cases](https://update.kbv.de/ita-update/Labor/Labordatenkommunikation/EXT_ITA_VGEX_LDT_3_2_19_Use_Cases.pdf)
- [KBV LDT3 3.2.18 complete specification (archive)](https://update.kbv.de/ita-update/Vorquartale/ita_update_2025_Q2/Labor/Labordatenkommunikation/EXT_ITA_VGEX_LDT%203_2_18_Gesamtdokument.pdf)
- [KBV historical LDT description](https://wiki.gematik.de/download/attachments/76611849/KBV_ITA_VGEX_Datensatzbeschreibung_LDT.pdf?api=v2&modificationDate=1616407222426&version=1)
