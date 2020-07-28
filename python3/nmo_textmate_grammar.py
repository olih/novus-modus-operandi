import os
import sys
import argparse
import re
import json
from enum import Enum, auto
from typing import List, Tuple, Dict, Set

if not (sys.version_info.major == 3 and sys.version_info.minor >= 5):
    print("This script requires Python 3.5 or higher!")
    print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

def strip_string_array(rawlines: str, sep=",")->List[str]:
    return [line.strip() for line in rawlines.split(sep) if line.strip() != ""]

def escape_re(value: str)->str:
    return value

class TmLowerDashNameField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[a-z][a-z0-9-]+"
        self.scope = "variable.parameter"

class TmEnumField:
    def __init__(self, name: str, keywords: List[str]):
        self.name = name
        self.match = "|".join(sorted(list(set([escape_re(k.strip()) for k in keywords]))))
        self.scope = "keyword.control"

class TmLangField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[a-z]{2}(-[a-z]{2, 3})?"
        self.scope = "constant.other.symbol"

class TmIdentifierField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = escape_re(value)
        self.scope = "entity.name.tag"

class TmSectionField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = escape_re(value)
        self.scope = "markup.heading.1"

class TmPunctuationField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = escape_re(value)
        self.scope = "punctuation.definition.separator"

class TmIntField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[+-]?[0-9]+"
        self.scope = "constant.numeric"

class TmFloatField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[+-][0-9]+[.][0-9]+"
        self.scope = "constant.numeric"

class TmFractionField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[+-]?[0-9]+/[1-9][0-9]*"
        self.scope = "constant.numeric"

class TmVersionField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[0-9]+[.][0-9]+[.][0-9]+"
        self.scope = "constant.numeric"

class TmUrlField:
    def __init__(self, name: str):
        self.name = name
        self.match = "https?://[^\\s]+"
        self.scope = "markup.underline.link"

class TmPathField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[^\\s:,;|@%^&*()+=]+"
        self.scope = "markup.italic"

class TmAnyStringField:
    def __init__(self, name: str):
        self.name = name
        self.match = ".{2,}"
        self.scope = "string"

class TmAnyStringButField:
    def __init__(self, name: str, but: str):
        self.name = name
        self.match = "[^{}]+".format(but)
        self.scope = "string"

class TmSeparatorField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = "\\b[{}]\\s?".format(escape_re(value))
        self.scope = "punctuation.separator.array"

    def to_tm_pattern(self, extName: str):
        return {
            "comment": "{}".format(self.name),
            "match": self.match,
            "name": "{}.{}".format(self.scope, extName)
        }

class TmArrayField:
    def __init__(self, name: str, start: str, finish: str, separator: str, altrows):
        self.name = name
        self.match = "[{}][^{}]*[{}]".format(start, start, finish)
        self.altrows = altrows
        self.scope = "markup.italic"
        self.separator = separator
    
    def to_tm_patterns(self, extName: str):
        separatorPattern = TmSeparatorField("separator", self.separator).to_tm_pattern(extName)
        return {
            "patterns": [separatorPattern] + [altrow.to_tm_rule(extName) for altrow in self.altrows]
        }


MEDIA_TYPES = ["html","json","json-ld","markdown","rdf","nt","ttl","csv"]
REQUIRE_SECTIONS = ["header", "fragments", "chunks", "accessors"]
REQUIRE_TYPES = strip_string_array("marker, enum, int, float, fraction, time, email, idstring, freetext, csvenum")
REQUIRE_STRING_CONSTRAINTS = strip_string_array("starts-with, ends-with, min-length, max-length, char-exp, followed-by, hash:sha-256, single-line, multiple-lines, AZ, az, digit, underscore, dash")
REQUIRE_NUMBER_CONSTRAINTS = strip_string_array("multiple-of, zero-pad, a < b, < _ <, < _ <=, <= _ <, <= _ <=, _ !=")
REQUIRE_LIST_CONSTRAINTS = strip_string_array("min-items, max-items")
REQUIRE_ACCESS_CONSTRAINTS = strip_string_array("editable, read-once, write-once, remote-check, hourly-write, daily-write, monthly-write, hourly-read, daily-read, monthly-read")
REQUIRE_GENERATORS = strip_string_array("elm-string-serializer, python-string-serializer, python-string-validator, slack-ui, vscode-syntax")

def paren(value: str)->str:
    return "({})".format(value)

class TmFieldRow:
    def __init__(self, name:str, isfullrow = True):
        self.name = name
        self.fields = []
        self.isfullrow = isfullrow
    
    def identifier(self, name: str, value: str):
        self.fields.append(TmIdentifierField(name, value))
        return self
    
    def id(self, name: str):
        return self.identifier(name, name)

    def section(self, name: str):
        section_name = "section {}".format(name)
        self.fields.append(TmSectionField(section_name, section_name))
        return self

    def customid(self, name: str):
        self.fields.append(TmLowerDashNameField(name))
        return self

    def path(self, name: str):
        self.fields.append(TmPathField(name))
        return self

    def lang(self):
        self.fields.append(TmLangField("language"))
        return self

    def colon(self):
        self.fields.append(TmPunctuationField("colon-separator", ":"))
        return self
    
    def arrow(self):
        self.fields.append(TmPunctuationField("arrow-separator", "->"))
        return self
    
    def emptyarray(self):
        self.fields.append(TmPunctuationField("empty-array", "\\[\\]"))
        return self

    def anystr(self, name: str):
        self.fields.append(TmAnyStringField(name))
        return self
    
    def anystrbutsep(self, name: str):
        self.fields.append(TmAnyStringButField(name, "\\|\\|"))
        return self

    def squarearr(self, name: str, subfields: List):
        self.fields.append(TmArrayField(name, "\\[", "\\]", ",", subfields))
        return self
    
    def pipearr(self, name: str, subfields: List):
        self.fields.append(TmArrayField(name, "\\[", "\\]", "\\|\\|", subfields))
        return self
    
    def mediatype(self):
        self.fields.append(TmEnumField("mediatype", MEDIA_TYPES))
        return self
    
    def requiretype(self):
        self.fields.append(TmEnumField("require-type", REQUIRE_TYPES))
        return self

    def stringconstr(self):
        self.fields.append(TmEnumField("string-constraint", REQUIRE_STRING_CONSTRAINTS))
        return self
    
    def numberconstr(self):
        self.fields.append(TmEnumField("number-constraint", REQUIRE_NUMBER_CONSTRAINTS))
        return self

    def listconstr(self):
        self.fields.append(TmEnumField("list-constraint", REQUIRE_LIST_CONSTRAINTS))
        return self
    
    def accessconstr(self):
        self.fields.append(TmEnumField("access-constraint", REQUIRE_ACCESS_CONSTRAINTS))
        return self
    
    def constraints(self, flags: str):
        constr = []
        if "S" in flags:
           constr +=  REQUIRE_STRING_CONSTRAINTS
        if "N" in flags:
           constr +=  REQUIRE_NUMBER_CONSTRAINTS
        if "L" in flags:
           constr +=  REQUIRE_LIST_CONSTRAINTS
        if "A" in flags:
           constr +=  REQUIRE_ACCESS_CONSTRAINTS
        self.fields.append(TmEnumField("access-".format(flags), constr))
        return self
        



    def requiresections(self):
        self.fields.append(TmEnumField("require-sections", REQUIRE_SECTIONS))
        return self
    
    def requiregenerators(self):
        self.fields.append(TmEnumField("require-generators", REQUIRE_GENERATORS))
        return self

    def url(self, name: str):
        self.fields.append(TmUrlField(name))
        return self
    
    def integer(self, name: str):
        self.fields.append(TmIntField(name))
        return self

    def version(self, name: str):
        self.fields.append(TmVersionField(name))
        return self

    def _to_match_rule(self)->str:
        matches = "[ ]*".join([paren(field.match) for field in self.fields])
        if self.isfullrow:
            return "^{}$".format(matches)
        else:
            return "{}".format(matches)

    def _to_captures_rule(self, extName: str):
        result = {}
        count = 0
        for field in self.fields:
            count = count + 1
            if "to_tm_patterns" in dir(field):
                result[str(count)] = field.to_tm_patterns(extName)
            else:
                name = "{}.{}".format(field.scope, extName)
                result[str(count)] = { "name": name}

        return result
    def _to_comment(self)->str:
        comment = " ".join([field.name for field in self.fields])
        return comment

    def to_tm_rule(self, extName: str):
        return {
            "comment": self._to_comment(),
            "match": self._to_match_rule(),
            "captures" : self._to_captures_rule(extName),
        }

    def singleton(self):
        return [self]


class TmFieldSection:
    def __init__(self, name:str):
        self.name = name
        self.headers = []
        self.rows = []
    
    def add_header(self, row: TmFieldRow):
        self.headers.append(row)
        return self
    
    def add_row(self, row: TmFieldRow):
        self.rows.append(row)
        return self

    def header(self, name: str):
        header = TmFieldRow(name)
        self.add_header(header)
        return header

    def row(self, name: str):
        row = TmFieldRow(name)
        self.add_row(row)
        return row

    def to_tm_patterns(self, extName: str):
        return {
            "patterns": [header.to_tm_rule(extName) for header in self.headers] + [row.to_tm_rule(extName) for row in self.rows]
        }

class TextMateGrammar:
    def __init__(self):
        self.schema = "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json"
        self.name = ""
        self.extName = ""
        self.filename = ""
        self.sections = []

    def set_name(self, name: str):
        self.name = name
        return self

    def set_extension(self, extName: str):
        self.extName = extName
        return self

    def add_section(self, section: TmFieldSection):
        self.sections.append(section)
        return self

    def _to_patterns_include(self):
        return [{"include": "#{}".format(section.name)} for section in self.sections ]
        
    def _to_repository(self):
        return { section.name:section.to_tm_patterns(self.extName) for section in self.sections }

    def to_obj(self):
        content = {
            "$schema": self.schema,
            "name": self.name,
            "patterns": self._to_patterns_include(),
            "repository": self._to_repository(),
            "scopeName": "source.{}".format(self.extName)
        }
        return content

    def set_filename(self, filename: str):
        self.filename = filename
        return self

    def save(self):
        with open(self.filename, 'w') as outfile:
            json.dump(self.to_obj(), outfile, indent=2)
 
def tm_array_type():
    return TmFieldRow("array-value", isfullrow = False)

headerSection = TmFieldSection("header")
headerSection.header("section header").section("header")
headerSection.row("id-urn").id("id-urn").colon().path("id-path")
headerSection.row("require-sections").id("require-sections").colon().squarearr("require-sections-values", tm_array_type().requiresections().version("section-version").singleton())
headerSection.row("prefixes").id("prefixes").colon().squarearr("prefixes-values", tm_array_type().customid("prefix").url("prefix-url").singleton())
headerSection.row("name").id("name").lang().colon().anystr("name-value")
headerSection.row("title").id("title").lang().colon().anystr("title-value")
headerSection.row("license").id("license").lang().colon().anystr("license-value")
headerSection.row("attribution-name").id("attribution-name").lang().colon().anystr("attribution-name-value")
headerSection.row("author").id("author").lang().colon().anystr("author-value")
headerSection.row("description").id("description").lang().colon().anystr("description-value")
headerSection.row("license-url").id("license-url").mediatype().lang().colon().url("license-url-value")
headerSection.row("author-url").id("author-url").mediatype().lang().colon().url("author-url-value")
headerSection.row("license-url").id("license-url").mediatype().lang().colon().url("license-url-value")
headerSection.row("attribution-url").id("attribution-url").mediatype().lang().colon().url("attribution-url-value")
headerSection.row("homepage-url").id("homepage-url").mediatype().lang().colon().url("homepage-url-value")
headerSection.row("repository-url").id("repository-url").mediatype().lang().colon().url("repository-url-value")
headerSection.row("copyright-year").id("copyright-year").colon().integer("copyright-year-value")
headerSection.row("require-types").id("require-types").colon().squarearr("type-arr", tm_array_type().requiretype().singleton())
headerSection.row("require-generators").id("require-generators").colon().squarearr("generator-arr", tm_array_type().requiregenerators().singleton())
headerSection.row("require-string-constraints").id("require-string-constraints").colon().squarearr("string-constraint-arr", tm_array_type().stringconstr().singleton())
headerSection.row("require-number-constraints").id("require-number-constraints").colon().squarearr("number-constraint-arr", tm_array_type().numberconstr().singleton())
headerSection.row("require-list-constraints").id("require-list-constraints").colon().squarearr("list-constraint-arr", tm_array_type().listconstr().singleton())
headerSection.row("require-access-constraints").id("require-access-constraints").colon().squarearr("access-constraint-arr", tm_array_type().accessconstr().singleton())


fragmentsSection = TmFieldSection("fragments")
fragmentsSection.header("section fragments").section("fragments")
fragmentsSection.row("marker").id("fragment").customid("fragment-id").id("marker").id("constraints").emptyarray().id("values").pipearr("values-arr", tm_array_type().anystrbutsep("str-value").singleton()).arrow().anystr("other")
fragmentsSection.row("enum").id("fragment").customid("fragment-id").id("enum").id("constraints").pipearr("constraint-arr", tm_array_type().constraints("A").singleton()).id("values").pipearr("values-arr", tm_array_type().anystrbutsep("str-value").singleton()).arrow().anystr("other")
fragmentsSection.row("int").id("fragment").customid("fragment-id").id("int").id("constraints").pipearr("constraint-arr", tm_array_type().constraints("AN").singleton()).arrow().anystr("other")
fragmentsSection.row("float").id("fragment").customid("fragment-id").id("float").id("constraints").pipearr("constraint-arr", tm_array_type().constraints("AN").singleton()).arrow().anystr("other")
fragmentsSection.row("fraction").id("fragment").customid("fragment-id").id("fraction").id("constraints").pipearr("constraint-arr", tm_array_type().constraints("AN").singleton()).arrow().anystr("other")
fragmentsSection.row("set[int]").id("fragment").customid("fragment-id").id("set\\[int\\]").id("constraints").pipearr("constraint-arr", tm_array_type().constraints("ANL").singleton()).arrow().anystr("other")
fragmentsSection.row("set[float]").id("fragment").customid("fragment-id").id("set\\[float\\]").id("constraints").pipearr("constraint-arr", tm_array_type().constraints("ANL").singleton()).arrow().anystr("other")
fragmentsSection.row("set[fraction]").id("fragment").customid("fragment-id").id("set\\[fraction\\]").id("constraints").pipearr("constraint-arr", tm_array_type().constraints("ANL").singleton()).arrow().anystr("other")
fragmentsSection.row("list[int]").id("fragment").customid("fragment-id").id("list\\[int\\]").id("constraints").pipearr("constraint-arr", tm_array_type().constraints("ANL").singleton()).arrow().anystr("other")
fragmentsSection.row("list[float]").id("fragment").customid("fragment-id").id("list\\[float\\]").id("constraints").pipearr("constraint-arr", tm_array_type().constraints("ANL").singleton()).arrow().anystr("other")
fragmentsSection.row("list[fraction]").id("fragment").customid("fragment-id").id("list\\[fraction\\]").id("constraints").pipearr("constraint-arr", tm_array_type().constraints("ANL").singleton()).arrow().anystr("other")

print("Saving Textmate grammar ...")
tmg=TextMateGrammar()
tmg.set_name("Novus Modus Operandi")
tmg.set_extension("nmo")
tmg.set_filename("../vscode/nmo/syntaxes/nmo.tmLanguage.json")
tmg.add_section(headerSection)
tmg.add_section(fragmentsSection)
tmg.save()