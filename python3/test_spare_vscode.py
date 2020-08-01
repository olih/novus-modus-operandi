import unittest
import re

from spare_vscode import create_my_section, create_my_grammar, simple_field, enum_field, line_field_seq, embed_field_seq, alt_field_seq

simple_field_obj = {
    'comment': 'simple-field',
    'match': '^(simple)$',
    'captures': {
        '1': {
            'comment': 'simple-field',
               'match': 'simple',
            'name': 'scope-simple-field.extension_name'
        }
    }
}
enum_field_obj = {
    'comment': 'enum-field',
    'match': '^(\\b(keyword|keyword1|keyword2)\\b)$',
    'captures': {
        '1': {
            'comment': 'enum-field',
               'match': '\\b(keyword|keyword1|keyword2)\\b',
            'name': 'scope.extension_name'
        }
    }
}

simple_field_enum_field_obj = {
    'comment': 'simple-field enum-field',
    'match': '^(simple)[ ]*(\\b(keyword|keyword1|keyword2)\\b)$',
    'captures': {
        '1': {
            'comment': 'simple-field',
            'match': 'simple',
            'name': 'scope-simple-field.extension_name'
        },
        '2': {
            'comment': 'enum-field',
            'match': '\\b(keyword|keyword1|keyword2)\\b',
            'name': 'scope.extension_name'}
    }
}

embedded_fields_obj = {
    'comment': 'simple-field alt-field-seq',
    'match': '^(simple)[ ]*(.*)$',
    'captures': {
        '1': {
             'comment': 'simple-field',
             'match': 'simple',
             'name': 'scope-simple-field.extension_name'},
        '2': {
            'patterns': [
                {'comment': 'simple-field',
                 'match': '(simple)',
                 'captures': {
                            '1': {
                                'comment': 'simple-field',
                                'match': 'simple',
                                'name': 'scope-simple-field.extension_name'
                            }
                 }
                 }
            ]
        }
    }
}

def group(matched):
    return matched.group() if matched else None

class TestSpareVsCode(unittest.TestCase):

    def test_simple_field(self):
        field = simple_field()
        p = re.compile(field.to_match())
        self.assertEqual(p.match("simple").group(), "simple")

    def test_enum_field(self):
        field = enum_field()
        p = re.compile(field.to_match())
        for k in ["keyword", "keyword1", "keyword2"]:
            with self.subTest(k=k):
                self.assertEqual(group(p.match(k)), k)

    def test_line_field_seq(self):
        field = line_field_seq([simple_field(), simple_field()])
        p = re.compile(field.to_match())
        self.assertEqual(p.match("simple simple").group(), "simple simple")

    def test_embed_field_seq(self):
        field = embed_field_seq([simple_field(), simple_field()])
        p = re.compile(field.to_match())
        self.assertEqual(p.match("simple simple").group(), "simple simple")

    def test_alt_field_seq(self):
        field = alt_field_seq([embed_field_seq([simple_field(), simple_field()])])
        p = re.compile(field.to_match())
        self.assertEqual(p.match("anything really").group(), "anything really")

    def test_create_my_section(self):
        my_section = create_my_section().to_tm_obj()
        self.assertEqual(len(my_section["patterns"]), 4)
        self.assertEqual(my_section["patterns"][0], simple_field_obj)
        self.assertEqual(my_section["patterns"][1], enum_field_obj)
        self.assertEqual(my_section["patterns"][2], simple_field_enum_field_obj)
        self.assertEqual(my_section["patterns"][3], embedded_fields_obj)

    def test_create_my_grammar(self):
        my_grammar = create_my_grammar().to_obj()
        self.assertEqual(my_grammar["name"], "my script language")
        self.assertEqual(my_grammar["scopeName"], "source.extension_name")
        self.assertEqual(my_grammar["patterns"], [{'include': '#section1'}])
        self.assertEqual(list(my_grammar["repository"].keys()), ["section1"])
       