from typing import List, Tuple, Dict, Set
from vscode_helper import TmConfig, TmBaseField, TmSimpleRegexField, TmEnumRegexField, TmFieldSequence, TmAltFieldSequence, TextMateGrammar


cfg = TmConfig().set_extension("extension_name")

def simple_field():
    return TmSimpleRegexField(
        cfg,
        name = "simple-field",
        scope = "scope-simple-field",
        match = "simple"
        )

def enum_field():
    return TmEnumRegexField(
        cfg,
        name = "enum-field",
        scope = "scope",
        keywords = ["keyword1", "keyword2"]
        )

def field_seq(fieldseq: List[TmBaseField]):
    return TmFieldSequence(
        cfg,
        name = "field-seq",
        start = "^",
        finish = "$",
        fieldseq = fieldseq
        )

def alt_field_seq(altfieldseq: List[TmFieldSequence]):
    return TmAltFieldSequence(
        cfg,
        name = "alt-field-seq",
        altfieldseq = altfieldseq
        )
        
def create_my_section():
    mySection = TmAltFieldSequence(cfg, "name", [])
    mySection.add(field_seq([simple_field()]))
    mySection.add(field_seq([enum_field()]))
    mySection.add(field_seq([simple_field(), enum_field()]))
    # mySection.row("custom-row").alt_field_seq(field_seq().simple_field())
    return mySection

