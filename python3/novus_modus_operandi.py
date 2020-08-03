import os
import sys
import argparse
import re
from typing import List, Tuple, Dict, Set
from enum import Enum, auto


if not (sys.version_info.major == 3 and sys.version_info.minor >= 5):
    print("This script requires Python 3.5 or higher!")
    print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)


def strip_string_array(rawlines: str, sep=",")->List[str]:
    return [line.strip() for line in rawlines.split(sep) if line.strip() != ""]

def parse_bracket_array(line: str)-> List[str]:
    return strip_string_array(line.replace("[", "").replace("]", ""), sep=",")

def parse_bracket_dict(line: str)-> Dict[str, str]:
    return { part.split(" ")[0]:part.split(" ")[1] for part in parse_bracket_array(line) }

def to_bracket_array(items: List[str], sep=",")->str:
    return "[ {} ]".format(sep.join(items))

def to_bracket_dict(keyvalues: Dict[str, str], sep=",")->str:
    return to_bracket_array(["{} {}".format(key, value) for key, value in keyvalues.items()], sep)

def strip_unknown(expected, lines):
    return [line for line in lines if expected in line]

def strip_empty(lines):
    return [line.strip() for line in lines if len(line.strip())>0]

def get_prefix(value:str)->str:
    return value.split(":", 2)[0]

class NMOHeaders:
    def __init__(self):
        self.id_urn = ""
        self.prefixes = { "github": "https://github.com/" }
        self.require_sections  = {i: "0.5" for i in ["header", "fragments", "chunks", "accessors"]}
        self.require_types  = set(["enum", "int", "float", "fraction" ])
        self.require_generators  = set(["elm-string-serializer", "python-string-serializer"])
        self.url_refs = { }
        self.text_refs = { }
        self.copyright_year = 3000

    def set_id_urn(self, value: str):
        self.id_urn = value
        return self

    def set_copyright_year(self, year: int):
        self.copyright_year = year
        return self

    def set_prefixes(self, prefixes: Dict[str, str]):
        self.prefixes = prefixes
        return self

    def set_require_sections(self, sections: Dict[str, str]):
        self.require_sections = sections
        return self

    def set_require_types(self, require_types: Set[str]):
        self.require_types = require_types
        return self
    
    def set_require_generators(self, require_generators: Set[str]):
        self.require_generators = require_generators
        return self

    def set_url(self, name: str, media_type: str, lang: str, url: str):
        self.url_refs[(name.strip(), media_type.strip(), lang.strip())] = url.strip()
        return self

    def get_url(self, name: str, media_type: str, lang: str, defaultValue = None):
        return self.url_refs.get((name.strip(), media_type.strip(), lang.strip()), defaultValue)

    def set_text(self, name: str,lang: str, text: str):
        self.text_refs[(name.strip(), lang.strip())] = text.strip()
        return self

    def get_text(self, name: str,lang: str, defaultValue = None):
        return self.text_refs.get((name.strip(), lang.strip()), defaultValue)

    @classmethod
    def from_string_list(cls, lines: str):
        result = cls()
        for line in lines:
            rawkey, rawvalue = line.split(":", 1)
            key = rawkey.strip()
            value = rawvalue.strip()
            if key == "id-urn":
                result.set_id_urn(value)
            elif key == "copyright-year":
                result.set_copyright_year(int(value))
            elif key == "prefixes":
                result.set_prefixes(parse_bracket_dict(value))
            elif key == "require-sections":
                result.set_require_sections(parse_bracket_dict(value))
            elif key == "require-types":
                result.set_require_types(set(parse_bracket_array(value)))
            elif key == "require-generators":
                result.set_require_generators(set(parse_bracket_array(value)))
            elif key.count(" ") == 1:
                name, lang = key.split()
                if name in ["license", "attribution-name", "author", "name" ,"title", "description", "alternative-title"]:
                    result.set_text(name, lang, value)
            elif key.count(" ") == 2:
                name, media_type, lang = key.split()
                supported_media = ["html", "json", "rdf", "markdown", "nt", "ttl", "json-ld", "csv"]
                if name in ["license-url", "attribution-url", "author-url", "metadata-url", "homepage-url", "repository-url", "content-url"] and media_type in supported_media:
                    result.set_url(name, media_type, lang, value)
            else:
                raise Exception("Header key [{}] is not supported".format(key))
        return result
    
    def to_string_list(self)->List[str]:
        results = []
        results.append("id-urn: {}".format(self.id_urn))
        results.append("require-sections: {}".format(to_bracket_dict(self.require_sections)))
        results.append("require-types: {}".format(to_bracket_array(sorted(list(self.require_types)))))
        results.append("require-generators: {}".format(to_bracket_array(sorted(list(self.require_generators)))))
        results.append("prefixes: {}".format(to_bracket_dict(self.prefixes)))
        for keydata, value in self.text_refs.items():
            results.append("{} {}: {}".format(keydata[0], keydata[1], value))
        for keydata, value in self.url_refs.items():
            results.append("{} {} {}: {}".format(keydata[0], keydata[1], keydata[2], value))
        results.append("copyright-year: {}".format(self.copyright_year))
        return results

    def to_string(self)->str:
        return "\n".join(self.to_string_list())

    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return self.to_string()
    
    def __eq__(self, other):
        thisone = (self.id_urn, self.copyright_year,  self.prefixes, self.require_sections, self.url_refs, self.text_refs, self.require_types, self.require_generators)
        otherone = (other.id_urn, other.copyright_year, other.prefixes, other.require_sections, other.url_refs, other.text_refs, other.require_types, other.require_generators)
        return thisone == otherone

    def get_short_prefixes(self)->Set[str]:
        return set([key for key, _ in self.prefixes.items()])

#  marker, enum, int, float, fraction, time, email, idstring, freetext, csvenum, url
class FragmentType(Enum):
    MARKER = auto()
    ENUM = auto()
    INT = auto()
    FLOAT = auto()
    FRACTION = auto()
    TIME = auto()
    EMAIL = auto()
    IDSTRING = auto()
    FREETEXT = auto()
    URL = auto()
    CSVENUM = auto()
    NOT_SUPPORTED = auto()
    
    @classmethod
    def from_string(cls, value: str):
        if value == "marker":
            return FragmentType.MARKER
        elif value == "enum":
            return FragmentType.ENUM
        elif value == "int":
            return FragmentType.INT
        elif value == "float":
            return FragmentType.FLOAT
        elif value == "fraction":
            return FragmentType.FRACTION
        elif value == "time":
            return FragmentType.TIME
        elif value == "email":
            return FragmentType.EMAIL
        elif value == "idstring":
            return FragmentType.IDSTRING
        elif value == "freetext":
            return FragmentType.FREETEXT
        elif value == "url":
            return FragmentType.URL
        elif value == "csvenum":
            return FragmentType.CSVENUM
        else:
            return FragmentType.NOT_SUPPORTED
    
    @classmethod
    def to_string(cls, value):
        if value == FragmentType.MARKER:
            return "marker"
        elif value == FragmentType.ENUM:
            return "enum"
        elif value == FragmentType.INT:
            return "int"
        elif value == FragmentType.FLOAT:
            return "float"
        elif value == FragmentType.FRACTION:
            return "fraction"
        elif value == FragmentType.TIME:
            return "time"
        elif value == FragmentType.EMAIL:
            return "email"
        elif value == FragmentType.IDSTRING:
            return "idstring"
        elif value == FragmentType.FREETEXT:
            return "freetext"
        elif value == FragmentType.URL:
            return "url"
        elif value == FragmentType.CSVENUM:
            return "csvenum"
        else:
            return "E"

class NMOConstraint:
    def __init__(self):
        self.aa = ""

class NMOValue:
    def __init__(self):
        self.aa = ""

class NMOFragment:
    def __init__(self, id: str, segmentType: FragmentType, constraints: List[NMOConstraint], values: List[NMOValue], description: str):
        self.id = id
        self.segmentType = segmentType
        self.constraints = constraints
        self.values = values
        self.description = description

    @classmethod
    def from_string(cls, line: str):
        cmd, fragmentId, fragmentType, constraintsKey, constraintsAndMore = line.split(" ", 4 )
        assert cmd == "fragment", line
        assert constraintsKey == "constraints", line
        
        return cls(brushid = brushId, xy = V2d.from_string(x + " " + y), scale = Fraction(scale), angle = Fraction(angle), tags = parse_dlmt_array(tagsInfo))

 