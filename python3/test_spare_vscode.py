import unittest

from spare_vscode import create_my_section

class TestSpareVsCode(unittest.TestCase):

    def test_create_my_section(self):
        my_section = create_my_section().to_tm_ob()
        print(my_section)
        self.assertEqual(my_section, {})
 