from typing import List, Tuple, Dict, Set
from vscode_helper import TmConfig, TmSimpleRegexField, TmEnumRegexField, TmFieldSequence, TmAltFieldSequence, TmBaseSection, TextMateGrammar


cfg = TmConfig().set_extension("extension_name")

class TmMyFieldSeq(TmFieldSequence):
    def __init__(self, name: str):
        super().__init__(cfg, name, "^", "$")

    def simple_field(self):
        field = TmSimpleRegexField(
            self.config,
            name = "simple-field",
            scope = "scope-simple-field",
            match = "simple"
            )
        self.add(field)
        return self

    def enum_field(self):
        field = TmEnumRegexField(
            self.config,
            name = "enum-field",
            scope = "scope",
            keywords = ["keyword1", "keyword2"]
            )
        self.add(field)
        return self

    def alt_field_seq(self, altfieldseq: List[TmFieldSequence]):
        field = TmAltFieldSequence(
            self.config,
            name = "alt-field-seq",
            altfieldseq = altfieldseq
            )
        self.add(field)
        return self
        
class TmMySection(TmBaseSection):
    def __init__(self, name:str):
        super().__init__(cfg, name)
    
    def header(self, name: str):
        header = TmMyFieldSeq(name)
        self.add_header(header)
        return header

    def row(self, name: str):
        row = TmMyFieldSeq(name)
        self.add_row(row)
        return row

def field_seq():
    return TmMyFieldSeq("seq")

def create_my_section():
    mySection = TmMySection("name")
    mySection.header("section mysection").simple_field().enum_field()
    mySection.row("row-simple-field").simple_field()
    mySection.row("row-enum-field").enum_field()
    mySection.row("row-simple-and-enum").simple_field().enum_field().simple_field()
    # mySection.row("custom-row").alt_field_seq(field_seq().simple_field())
    return mySection

