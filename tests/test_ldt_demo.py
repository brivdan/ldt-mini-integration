import unittest
from pathlib import Path
from ldt_demo import encode_field, parse_fields, process

ROOT = Path(__file__).resolve().parents[1]

class LDTTests(unittest.TestCase):
    def test_length_prefix_and_roundtrip(self):
        raw = encode_field('8000', '8205')
        self.assertEqual(raw, b'01380008205\r\n')
        self.assertEqual(parse_fields(raw)[0].value, '8205')

    def test_both_versions_map_to_same_data(self):
        a = process(ROOT/'samples/ldt2_demo.ldt', 'ldt2')
        b = process(ROOT/'samples/ldt3_demo.ldt', 'ldt3')
        self.assertEqual(a, b)
        self.assertEqual(a['observation']['value'], '95')

    def test_invalid_length_rejected(self):
        with self.assertRaises(ValueError):
            parse_fields(b'01280008205\r\n')

    def test_unclosed_object_rejected(self):
        p = ROOT/'samples/ldt3_demo.ldt'
        from ldt_demo import read_ldt3
        fields = parse_fields(p.read_bytes())
        with self.assertRaises(ValueError):
            read_ldt3(fields[:-1])

if __name__ == '__main__':
    unittest.main()
