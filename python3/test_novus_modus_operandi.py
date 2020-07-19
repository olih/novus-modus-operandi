import unittest

from novus_modus_operandi import NMOHeaders

class TestNMOHeaders(unittest.TestCase):

    def test_convert(self):
        headers = NMOHeaders()
        headers.set_prefixes({ "prefix1": "http://domain1.com", "prefix2": "http://domain2.com"})
        headers.set_text("license", "en", "Creative Commons")
        headers.set_text("license", "fr", "Creative Communs")
        headers.set_text("title", "en", "Some english title")
        headers.set_text("title", "fr", "Titre en francais")
        headers.set_require_types(set(["boolean", "type2"]))
        headers.set_require_generators(set(["gen1", "gen3"]))
        headers.set_id_urn("company/project/123")
        headers.set_copyright_year(2020)
        self.assertEqual(NMOHeaders.from_string_list(headers.to_string_list()), headers)