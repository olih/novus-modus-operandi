import unittest
from random import randint, choice
from typing import List, Tuple, Dict, Set, Optional
from spare_dsl import SpareRow, SpareItem, SpareRowParser
from dsl_text import ParsingContext
from examples import Examples
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
emailExamples = Examples().load("{}/examples/emails.ex.json".format(dir_path))

spareRowParser = SpareRowParser()
ctx = ParsingContext().set_id("ctx7").set_line_number(27)
class TestParsingSpareRow(unittest.TestCase):

    def test_conversion_should_succeed(self):
        examples = [
            SpareRow()
                .set_id("one")
                .set_v_int(15)
                .set_tags(set(["monday", "tuesday"]))
                .set_emails(emailExamples.sample_valid(3))
                .set_url("http://cc.org")
                .set_color_name_as_str("green")
                .set_items([SpareItem().set_v_float(1.3).set_v_fraction_as_str("1/4"), SpareItem().set_v_float(1.7).set_v_fraction_as_str("1/5")])
                .set_description("some description")
            ]
        for ex in examples:
                line = ex.to_nmo_string()
                spareRow = spareRowParser.parse(ctx, line)
                with self.subTest(ex=ex):
                    self.assertEqual(ex, spareRow)
