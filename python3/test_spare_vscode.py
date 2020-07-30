import unittest

from spare_vscode import create_my_section

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


class TestSpareVsCode(unittest.TestCase):

    def test_create_my_section(self):
        my_section = create_my_section().to_tm_obj()
        print(my_section["patterns"][1])
        self.assertEqual(len(my_section["patterns"]), 4)
        self.assertEqual(my_section["patterns"][0], simple_field_enum_field)
        self.assertEqual(my_section["patterns"][1], simple_field)
