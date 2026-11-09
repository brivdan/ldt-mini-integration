"""Educational subset of LDT2 and LDT3; NOT a KBV-compliant implementation."""
from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Field:
    code: str
    value: str


def encode_field(code: str, value: str) -> bytes:
    """LDT/xDT field: 3 ASCII length digits, 4-digit code, value, CRLF.
    Length is the number of bytes of the entire line (including CRLF).
    """
    if len(code) != 4 or not code.isdigit():
        raise ValueError(f"Invalid field code: {code!r}")
    payload = code.encode('ascii') + value.encode('latin-1') + b'\r\n'
    length = len(payload) + 3
    if length > 999:
        raise ValueError("Field is too long for three-digit length")
    return f'{length:03d}'.encode('ascii') + payload


def parse_fields(data: bytes) -> list[Field]:
    fields = []
    pos = 0
    while pos < len(data):
        if pos + 3 > len(data) or not data[pos:pos+3].isdigit():
            raise ValueError(f"Invalid length prefix at byte {pos}")
        size = int(data[pos:pos+3])
        if size < 9 or pos + size > len(data):
            raise ValueError(f"Invalid field length {size} at byte {pos}")
        line = data[pos:pos+size]
        if not line.endswith(b'\r\n'):
            raise ValueError(f"Missing CRLF at byte {pos}")
        code = line[3:7].decode('ascii')
        if not code.isdigit():
            raise ValueError(f"Invalid field ID at byte {pos}")
        value = line[7:-2].decode('latin-1')
        fields.append(Field(code, value))
        pos += size
    return fields


def require_one(fields: list[Field], code: str) -> str:
    matches = [f.value for f in fields if f.code == code]
    if len(matches) != 1 or not matches[0]:
        raise ValueError(f"Expected exactly one nonempty {code}, found {len(matches)}")
    return matches[0]


def read_ldt2(fields: list[Field]) -> dict:
    """Teaching subset: one report, one patient, one observation."""
    if not fields or fields[0] != Field('8000', '8205'):
        raise ValueError('Expected an LDT2-style 8205 report')
    if any(f.code in ('8002', '8003') for f in fields):
        raise ValueError('Unexpected LDT3 object field in LDT2 sample')
    return build_report(fields, fields)


def read_ldt3(fields: list[Field]) -> dict:
    """Teaching subset: LDT3 object boundaries for patient and result."""
    if not fields or fields[0] != Field('8000', '8205'):
        raise ValueError('Expected an LDT3-style 8205 report')
    objects = {}
    stack: list[tuple[str, list[Field]]] = []
    for f in fields[1:]:
        if f.code == '8002':
            stack.append((f.value, []))
        elif f.code == '8003':
            if not stack or stack[-1][0] != f.value:
                raise ValueError(f'Unmatched object close {f.value}')
            obj_name, contents = stack.pop()
            objects.setdefault(obj_name, []).append(contents)
        elif stack:
            stack[-1][1].append(f)
    if stack:
        raise ValueError('Unclosed LDT3 object')
    if len(objects.get('Obj_0047', [])) != 1 or len(objects.get('Obj_0060', [])) != 1:
        raise ValueError('This demo expects one patient Obj_0047 and one chemistry Obj_0060')
    return build_report(objects['Obj_0047'][0], objects['Obj_0060'][0])


def build_report(patient: list[Field], observation: list[Field]) -> dict:
    result = require_one(observation, '8420')
    try:
        float(result.replace(',', '.'))
    except ValueError as exc:
        raise ValueError('This demo only handles numeric results') from exc
    return {
        'patient': {
            'family_name': require_one(patient, '3101'),
            'given_name': require_one(patient, '3102'),
            'birth_date_ddmmyyyy': require_one(patient, '3103'),
        },
        'observation': {
            'test_code': require_one(observation, '8410'),
            'test_name': require_one(observation, '8411'),
            'value': result,
            'unit': require_one(observation, '8421'),
        },
    }


def process(path: Path, fmt: str) -> dict:
    fields = parse_fields(path.read_bytes())
    return (read_ldt2 if fmt == 'ldt2' else read_ldt3)(fields)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('format', choices=['ldt2', 'ldt3'])
    p.add_argument('file', type=Path)
    args = p.parse_args()
    print(json.dumps(process(args.file, args.format), indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
