"""
Unit tests for Gujarati Legacy Font Converter.
"""

import unittest
from core.font_converter import font_converter


class TestGujaratiFontConverter(unittest.TestCase):

    def test_legacy_detection(self):
        legacy_sample = "þw»f rðMŒkh{kt ƒk„kÞŒe …kfku™e ¾uŒe"
        self.assertTrue(font_converter.is_legacy_encoded(legacy_sample))

        unicode_sample = "શુષ્ક વિસ્તારમાં બાગાયતી પાકોની ખેતી"
        self.assertFalse(font_converter.is_legacy_encoded(unicode_sample))

        plain_english = "Today's mandi price for cotton in Rajkot is Rs 1500."
        self.assertFalse(font_converter.is_legacy_encoded(plain_english))

    def test_unicode_conversion(self):
        sample = "þw»f rðMŒkh{kt ƒk„kÞŒe …kfku™e ¾uŒe"
        converted = font_converter.convert_to_unicode(sample)
        self.assertIn("શુષ્ક", converted)
        self.assertIn("વિસ્તારમાં", converted)
        self.assertIn("બાગાયતી", converted)
        self.assertIn("પાકોની", converted)
        self.assertIn("ખેતી", converted)

    def test_crop_names_conversion(self):
        samples = [
            ("‚eŒkV¤", "સીતાફળ"),
            ("ƒkuh", "બોર"),
            ("yk{¤k", "આમળા"),
            ("‚h„ðku", "સરગવો"),
            ("ƒe÷e", "બીલી"),
            ("òtƒw", "જાંબુ"),
            ("ytSh", "અંજીર"),
            ("„wtËk", "ગુંદા"),
            ("fh{Ëk", "કરમદા"),
        ]
        for legacy, expected in samples:
            res = font_converter.convert_to_unicode(legacy)
            self.assertIn(expected, res, f"Failed converting {legacy} -> {expected}, got {res}")


if __name__ == "__main__":
    unittest.main()
