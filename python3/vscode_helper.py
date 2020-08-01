from typing import List, Tuple, Dict, Set
import re
import json

def escape_re(value: str)->str:
    return value

def paren(value: str)->str:
    return "({})".format(value)

def ensure_re(value: str):
    re.compile(value)
    return value
 
class TmConfig:
    def __init__(self):
        self.name = ""
        self.extname = ""
        self.schema = "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json"
        self.filename = ""
    
    def set_name(self, name: str):
        self.name = name
        return self

    def set_extension(self, extname: str):
        self.extname = extname
        return self

    def set_filename(self, filename: str):
        self.filename = filename
        return self

class TmBaseField:
    def to_match(self)->str:
        pass
    
    def to_comment(self)->str:
        pass
    
    def to_tm_obj(self):
        pass

    def singleton(self):
        return [self]


class TmSimpleRegexField(TmBaseField):
    def __init__(self, config: TmConfig, name: str, scope: str, match: str):
        self.config = config
        self.name = name
        self.match = ensure_re(match)
        self.scope = scope

    def to_match(self):
        return self.match
    
    def to_comment(self):
        return "{}".format(self.name)

    def to_tm_obj(self):
        return {
            "comment": self.to_comment(),
            "match": self.match,
            "name": "{}.{}".format(self.scope, self.config.extname)
        }

class TmEnumField(TmBaseField):
    def __init__(self, config: TmConfig, name: str, scope: str, keywords: List[str]):
        self.config = config
        self.name = name
        self.keywords = keywords
        self.scope = scope
    
    def to_match(self)->str:
        joined = "|".join(sorted(list(set([escape_re(k.strip()) for k in self.keywords]))))
        return "\\b({})\\b".format(joined)

    def to_comment(self):
        return "{}".format(self.name)

    def to_tm_obj(self)->str:
        return {
            "comment": self.to_comment(),
            "match": self.to_match(),
            "name": "{}.{}".format(self.scope, self.config.extname)
        }

class TmFieldSequence(TmBaseField):
    def __init__(self, config: TmConfig, name: str, start: str, finish: str, fieldseq: List[TmBaseField]) :
        self.config = config
        self.name = name
        self.start = ensure_re(start)
        self.finish = ensure_re(finish)
        self.fieldseq = fieldseq
    
    def add(self, field: TmBaseField):
        self.fieldseq.append(field)
        return self

    def to_match(self)->str:
        match_seq = "[ ]*".join([paren(field.to_match()) for field in self.fieldseq])
        match = "{}{}{}".format(self.start, match_seq, self.finish)
        return match

    def _to_captures_rule(self):
        result = {}
        count = 0
        for field in self.fieldseq:
            count = count + 1
            result[str(count)] = field.to_tm_obj()
        return result
    
    def to_comment(self)->str:
        comment = " ".join([field.to_comment() for field in self.fieldseq])
        return comment

    def to_tm_obj(self):
        return {
            "comment": self.to_comment(),
            "match": self.to_match(),
            "captures" : self._to_captures_rule(),
        }
    
    def singleton(self):
        return [self]

class TmAltFieldSequence(TmBaseField):
    def __init__(self, config: TmConfig, name: str, altfieldseq: List[TmFieldSequence]) :
        self.config = config
        self.name = name
        self.altfieldseq = altfieldseq

    def add(self, fieldseq: TmFieldSequence):
        self.altfieldseq.append(fieldseq)
        return self
    
    def to_match(self):
        return ".*"
    
    def to_comment(self):
        return "{}".format(self.name)

    def to_tm_obj(self):
        return {
            "patterns": [fieldseq.to_tm_obj() for fieldseq in self.altfieldseq]
        }

class TextMateGrammar:
    def __init__(self, config: TmConfig):
        self.config: TmConfig = config
        self.sections: List[TmAltFieldSequence] = [] 

    def add_section(self, section: TmAltFieldSequence):
        self.sections.append(section)
        return self

    def _to_patterns_include(self):
        return [{"include": "#{}".format(section.name)} for section in self.sections ]
        
    def _to_repository(self):
        return { section.name:section.to_tm_obj() for section in self.sections }

    def to_obj(self):
        content = {
            "$schema": self.config.schema,
            "name": self.config.name,
            "patterns": self._to_patterns_include(),
            "repository": self._to_repository(),
            "scopeName": "source.{}".format(self.config.extname)
        }
        return content

    def save(self):
        with open(self.config.filename, 'w') as outfile:
            json.dump(self.to_obj(), outfile, indent=2)
