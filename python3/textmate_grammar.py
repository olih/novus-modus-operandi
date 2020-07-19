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
    def __init__(self, name: str, keywords: List[str]):
        self.name = name
        self.match = "[a-z]{2}(-[a-z]{2, 3})?"

class TmPunctuationField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = re.escape(value)

class TmIntField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = "[+-]?[0-9]+"

class TmFloatField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = "[+-][0-9]+[.][0-9]+"

class TmFractionField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = "[+-]?[0-9]+/[1-9][0-9]*"

class TmUrlField:
    def __init__(self, name: str, value: str):
        self.name = name
        self.match = "https?://[^\\s]+"


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
            "match": self.match
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
    
        