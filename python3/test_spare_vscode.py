import unittest

from spare_vscode import create_my_section, create_my_grammar

simple_field = {
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
enum_field = {
    'comment': 'enum-field',
    'match': '^(keyword1|keyword2)$',
    'captures': {
        '1': {
            'comment': 'enum-field',
               'match': 'keyword1|keyword2',
            'name': 'scope.extension_name'
        }
    }
}

simple_field_enum_field = {
    'comment': 'simple-field enum-field',
    'match': '^(simple)[ ]*(keyword1|keyword2)$',
    'captures': {
        '1': {
            'comment': 'simple-field',
            'match': 'simple',
            'name': 'scope-simple-field.extension_name'
        },
        '2': {
            'comment': 'enum-field',
            'match': 'keyword1|keyword2',
            'name': 'scope.extension_name'}
    }
}

embedded_fields = {
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


class TestSpareVsCode(unittest.TestCase):

    def test_create_my_section(self):
        my_section = create_my_section().to_tm_obj()
        self.assertEqual(len(my_section["patterns"]), 4)
        self.assertEqual(my_section["patterns"][0], simple_field)
        self.assertEqual(my_section["patterns"][1], enum_field)
        self.assertEqual(my_section["patterns"][2], simple_field_enum_field)
        self.assertEqual(my_section["patterns"][3], embedded_fields)

    def test_create_my_grammar(self):
        my_grammar = create_my_grammar().to_obj()
        self.assertEqual(my_grammar["name"], "my script language")
        self.assertEqual(my_grammar["scopeName"], "source.extension_name")
        self.assertEqual(my_grammar["patterns"], [{'include': '#section1'}])
        self.assertEqual(list(my_grammar["repository"].keys()), ["section1"])
       