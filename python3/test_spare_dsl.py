import unittest
from random import randint, uniform, choice
from fractions import Fraction
from typing import List, Tuple, Dict, Set, Optional
from spare_dsl import SpareRow, SpareItem, SpareRowParser, SpareSection, SpareSectionParser, SpareSectionType, SpareDoc, SpareParser
from dsl_text import ParsingContext
from examples import Examples
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
emailExamples = Examples().load("{}/examples/emails.ex.json".format(dir_path))
urlExamples = Examples().load("{}/examples/urls.ex.json".format(dir_path))

spareRowParser = SpareRowParser()
spareSectionParser = SpareSectionParser()
spareParser = SpareParser()
ctx = ParsingContext().set_id("ctx7").set_line_number(27)

def rand_fract_str():
    return str(Fraction(randint(0, 1000), randint(1, 1000)))

def gen_row() -> SpareRow:
    row =  SpareRow()
    row.set_id("one")
    row.set_v_int(randint(1, 1000))
    row.set_tags(set(["monday", "tuesday"]))
    row.set_emails(emailExamples.sample_valid(3))
    row.set_url(urlExamples.pick_valid())
    row.set_color_name_as_str("green")
    row.set_items([SpareItem().set_v_float(uniform(1, 500)).set_v_fraction_as_str("1/4"), SpareItem().set_v_float(uniform(1, 500)).set_v_fraction_as_str("1/5")])
    row.set_description("some description")
    return row

def gen_spare_doc()->SpareDoc:
    spareDoc = SpareDoc()
    spareDoc.section_alpha.set_header(SpareSection().set_section_type(SpareSectionType.ALPHA))
    for _ in range(randint(1, 9)):
        spareDoc.section_alpha.add_row(gen_row())
    spareDoc.section_beta.set_header1(SpareSection().set_section_type(SpareSectionType.BETA))
    for _ in range(randint(0, 3)):
        spareDoc.section_beta.add_row(gen_row())
    return spareDoc

   

class TestParsingSpareRow(unittest.TestCase):
    
    def test_convert_spare_section_should_succeed(self):
        examples = [
            SpareSection().set_section_type(SpareSectionType.ALPHA),
            SpareSection().set_section_type(SpareSectionType.BETA)
        ]
        for ex in examples:
            line = ex.to_nmo_string()
            spareSection = spareSectionParser.parse(ctx, line)
            with self.subTest(ex=ex):
                self.assertEqual(ex, spareSection)

    def test_convert_spare_row_should_succeed(self):
        examples = [ gen_row() for _ in range(5)]
        for ex in examples:
            line = ex.to_nmo_string()
            spareRow = spareRowParser.parse(ctx, line)
            with self.subTest(ex=ex):
                self.assertEqual(ex, spareRow)


    def test_convert_spare_doc_should_succeed(self):
        examples = [ gen_spare_doc() for _ in range(12)]
        for ex in examples:
            filecontent = ex.to_nmo_string()
            spareDoc = spareParser.parse(ctx, filecontent)
            with self.subTest(ex=len(filecontent)):
                self.assertEqual(ex.to_nmo_string_list(), spareDoc.to_nmo_string_list())
