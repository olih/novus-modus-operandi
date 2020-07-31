from typing import List, Tuple, Dict, Set
from vscode_helper import TmConfig, TmBaseField, TmSimpleRegexField, TmEnumField, TmFieldSequence, TmAltFieldSequence, TextMateGrammar


cfg = TmConfig().set_extension("extension_name")

def simple_field():
    return TmSimpleRegexField(
        cfg,
        name = "simple-field",
        scope = "scope-simple-field",
        match = "simple"
        )

def enum_field():
    return TmEnumField(
        cfg,
        name = "enum-field",
        scope = "scope",
        keywords = ["keyword1", "keyword2"]
        )

def line_field_seq(fieldseq: List[TmBaseField]):
    return TmFieldSequence(
        cfg,
        name = "field-seq",
        start = "^",
        finish = "$",
        fieldseq = fieldseq
        )

def embed_field_seq(fieldseq: List[TmBaseField]):
    return TmFieldSequence(
        cfg,
        name = "field-seq",
        start = "",
        finish = "",
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
    mySection.add(line_field_seq([simple_field()]))
    mySection.add(line_field_seq([enum_field()]))
    mySection.add(line_field_seq([simple_field(), enum_field()]))
    myAternative = embed_field_seq([simple_field()])
    myAlternatives = alt_field_seq([myAternative])
    mySection.add(line_field_seq([simple_field(),myAlternatives ]))
    return mySection

