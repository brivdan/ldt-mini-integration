"""Convert the educational LDT2/LDT3 samples to XML.

Uses ldt_demo.py for decoding, field validation and mapping. These samples
are not full KBV-compliant LDT implementations.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

from ldt_demo import process


def to_xml(report: dict, source_format: str) -> bytes:
    """Serialize the normalized sample report as UTF-8, indented XML."""
    root = ET.Element("LabReport", {"sourceFormat": source_format.upper()})
    patient = ET.SubElement(root, "Patient")
    for tag, key in (
        ("FamilyName", "family_name"),
        ("GivenName", "given_name"),
        ("BirthDateDDMMYYYY", "birth_date_ddmmyyyy"),
    ):
        ET.SubElement(patient, tag).text = report["patient"][key]

    observation = ET.SubElement(root, "Observation")
    for tag, key in (
        ("TestCode", "test_code"),
        ("TestName", "test_name"),
        ("Value", "value"),
        ("Unit", "unit"),
    ):
        ET.SubElement(observation, tag).text = report["observation"][key]

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("format", choices=["ldt2", "ldt3"], help="Source format")
    parser.add_argument("file", type=Path, help="Input .ldt file")
    parser.add_argument("--output", "-o", type=Path, help="Save XML to this file; otherwise print it")
    args = parser.parse_args()

    try:
        report = process(args.file, args.format)
        output = to_xml(report, args.format)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(output)
            print(f"Wrote {args.output}", file=sys.stderr)
        else:
            sys.stdout.buffer.write(output)
    except (OSError, ValueError, KeyError) as exc:
        print(f"Conversion failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
