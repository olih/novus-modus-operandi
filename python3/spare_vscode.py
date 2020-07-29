from typing import List, Tuple, Dict, Set
from vscode_helper import TmConfig, TmSimpleRegexField, TmEnumRegexField, TmFieldSequence, TmAltFieldSequence


cfg = TmConfig().set_extension("extension_name")

class TmFieldRow:
    def __init__(self, name: str):
        self.fieldseq = TmFieldSequence(cfg, name, "^", "$")

    def simple_field(self):
        field = TmSimpleRegexField(
            self.fieldseq.config,
            name = "name",
            scope = "scope",
            match = "match"
            )
        return self.fieldseq.add(field)

    def enum_field(self):
        field = TmEnumRegexField(
            self.fieldseq.config,
            name = "name",
            scope = "scope",
            keywords = []
            )
        return self.fieldseq.add(field)

    def alt_field_seq(self, altfieldseq: List[TmFieldSequence]):
        field = TmAltFieldSequence(
            self.fieldseq.config,
            name = "name",
            start = "start",
            finish = "finish",
            altfieldseq = altfieldseq
            )
        return self.fieldseq.add(field)
        
 
