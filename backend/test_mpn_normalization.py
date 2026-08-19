import unittest
from decimal import Decimal
from pathlib import Path
from app.services.dataset_evaluation_service import normalize_mpn_identifier, load_rows
class MpnNormalizationTests(unittest.TestCase):
    def test_alphanumeric(self):
        self.assertEqual(normalize_mpn_identifier("ADR5117512CG"), "ADR5117512CG")
    def test_integer_excel_value(self):
        self.assertEqual(normalize_mpn_identifier(543143912), "543143912")
    def test_whole_number_float(self):
        self.assertEqual(normalize_mpn_identifier(543076916.0), "543076916")
    def test_leading_zero_string(self):
        self.assertEqual(normalize_mpn_identifier("00123456"), "00123456")
    def test_blank(self):
        self.assertEqual(normalize_mpn_identifier(None), "")
    def test_existing_string(self):
        self.assertEqual(normalize_mpn_identifier("SN74LS00N"), "SN74LS00N")
    def test_decimal_whole_number(self):
        self.assertEqual(normalize_mpn_identifier(Decimal("1516876.0")), "1516876")

if __name__ == "__main__":
    unittest.main()
