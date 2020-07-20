import os
import sys
import argparse
import re
from enum import Enum, auto
from typing import List, Tuple, Dict, Set

if not (sys.version_info.major == 3 and sys.version_info.minor >= 5):
    print("This script requires Python 3.5 or higher!")
    print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

class TmLowerDashNameField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[a-z][a-z0-9-]+"

class TmEnumField:
    def __init__(self, name: str, keywords: List[str]):
        self.name = name
        self.match = "|".join(sorted(list(set([re.escape(k.strip()) for k in keywords]))))

class TmLangField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[a-z]{2}(-[a-z]{2, 3})?"

class TmIdentifierField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = re.escape(value)

class TmPunctuationField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = re.escape(value)

class TmIntField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[+-]?[0-9]+"

class TmFloatField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[+-][0-9]+[.][0-9]+"

class TmFractionField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[+-]?[0-9]+/[1-9][0-9]*"

class TmUrlField:
    def __init__(self, name: str):
        self.name = name
        self.match = "https?://[^\\s]+"

class TmPathField:
    def __init__(self, name: str):
        self.name = name
        self.match = "[^\\s:,;|@%^&*()[]+=]+"

class TmEndStringField:
    def __init__(self, name: str):
        self.name = name
        self.match = ".{2,}$"

class TmFieldRow:
    def __init__(self, name:str):
        self.name = name
        self.fields = []
    
    def identifier(self, name: str, value: str):
        self.fields.append(TmIdentifierField(name, value))
        return self
    
    def id(self, name: str):
        return self.identifier(name, name)

    def path(self, name: str):
        self.fields.append(TmPathField(name))
        return self

    def lang(self):
        self.fields.append(TmLangField("language"))
        return self

    def colon(self):
        self.fields.append(TmPunctuationField("colon-separator", ":"))
        return self

    def endstr(self, name: str):
        self.fields.append(TmEndStringField(name))
        return self
    
    def mediatype(self):
        self.fields.append(TmEnumField("mediatype", ["html","json","json-ld","markdown","rdf","nt","ttl","csv"]))
        return self
    
    def url(self, name: str):
        self.fields.append(TmUrlField(name))
        return self
    
    def integer(self, name: str):
        self.fields.append(TmIntField(name))
        return self


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


headerSection = TmFieldSection("header")
headerSection.header("section header").id("section header")
headerSection.row("id-urn").id("id-urn").colon().path("id-path")
headerSection.row("require-sections").id("require-sections").colon().endstr("require-sections-values")
headerSection.row("prefixes").id("prefixes").colon().endstr("prefixes-values")
headerSection.row("name").id("name").lang().colon().endstr("name-value")
headerSection.row("title").id("title").lang().colon().endstr("title-value")
headerSection.row("license").id("license").lang().colon().endstr("license-value")
headerSection.row("attribution-name").id("attribution-name").lang().colon().endstr("attribution-name-value")
headerSection.row("author").id("author").lang().colon().endstr("author-value")
headerSection.row("description").id("description").lang().colon().endstr("description-value")
headerSection.row("license-url").id("license-url").mediatype().lang().colon().url("license-url-value")
headerSection.row("author-url").id("author-url").mediatype().lang().colon().url("author-url-value")
headerSection.row("license-url").id("license-url").mediatype().lang().colon().url("license-url-value")
headerSection.row("attribution-url").id("attribution-url").mediatype().lang().colon().url("attribution-url-value")
headerSection.row("homepage-url").id("homepage-url").mediatype().lang().colon().url("homepage-url-value")
headerSection.row("repository-url").id("repository-url").mediatype().lang().colon().url("repository-url-value")
headerSection.row("copyright-year").id("copyright-year").colon().integer("copyright-year-value")
headerSection.row("require-types").id("require-types").colon().endstr("require-types-values")
headerSection.row("require-generators").id("require-generators").colon().endstr("require-generators-values")


class TmLineMatcher:
    def __init__(self, name: str):
        self.name = name
        self.match = ""
    
    def set_match_keywords(self, keywords: List[str]):
        sorted_kw = sorted(list(set([re.escape(k.strip()) for k in keywords])))
        self.match = "\\b{}\\b".format("|".join(sorted_kw))
        return self
    
    def to_obj(self):
        return {
            "name": self.name,
            "match": self.match
        }

class TmLineCapturer:
    def __init__(self, name: str):
        self.name = name
        self.match = ""
        self.captures = {}
    
    def set_match_keywords(self, keywords: List[str]):
        sorted_kw = sorted(list(set([re.escape(k.strip()) for k in keywords])))
        self.match = "\\b{}\\b".format("|".join(sorted_kw))
        return self
    
    def to_obj(self):
        return {
            "name": self.name,
            "match": self.match,
            "captures": self.captures
        }


class TextMatePatterns:
    def __init__(self, name: str, patterns: List):
        self.name = name
        self.patterns = patterns

class TextMateGrammar:
    def __init__(self):
        self.name = ""
        self.extName = ""
        self.schema = "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json"

    def to_obj(self):
        content = {
            "$schema": self.schema,
            "name": self.name,
            "scopeName": "source.{}".format(self.extName)
        }
        return content
    
        