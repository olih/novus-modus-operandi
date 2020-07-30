from typing import List, Tuple, Dict, Set
import json

def escape_re(value: str)->str:
    return value

def paren(value: str)->str:
    return "({})".format(value)

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
    def to_tm_obj(self):
        pass

    def singleton(self):
        return [self]


class TmSimpleRegexField(TmBaseField):
    def __init__(self, config: TmConfig, name: str, scope: str, match: str):
        self.config = config
        self.name = name
        self.match = match
        self.scope = scope

    def to_tm_obj(self):
        return {
            "comment": "{}".format(self.name),
            "match": self.match,
            "name": "{}.{}".format(self.scope, self.config.extname)
        }

class TmEnumRegexField(TmBaseField):
    def __init__(self, config: TmConfig, name: str, scope: str, keywords: List[str]):
        self.config = config
        self.name = name
        self.keywords = keywords
        self.scope = scope

    def to_tm_obj(self):
        return {
            "comment": "{}".format(self.name),
            "match": "|".join(sorted(list(set([escape_re(k.strip()) for k in self.keywords])))),
            "name": "{}.{}".format(self.scope, self.config.extname)
        }

class TmFieldSequence(TmBaseField):
    def __init__(self, config: TmConfig, name: str, start: str, finish: str) :
        self.config = config
        self.name = name
        self.start = start
        self.finish = finish
        self.fieldseq = []
    
    def add(self, field: TmBaseField):
        self.fieldseq.append(field)
        return self

    def _to_match_rule(self)->str:
        match_seq = "[ ]*".join([paren(field.to_tm_obj()["match"]) for field in self.fieldseq])
        match = "{}{}{}".format(escape_re(self.start), match_seq, escape_re(self.finish))
        return match

    def _to_captures_rule(self):
        result = {}
        count = 0
        for field in self.fieldseq:
            count = count + 1
            result[str(count)] = field.to_tm_obj()
        return result
    
    def _to_comment(self)->str:
        comment = " ".join([field.to_tm_obj()["comment"] for field in self.fieldseq])
        return comment

    def to_tm_obj(self):
        return {
            "comment": self._to_comment(),
            "match": self._to_match_rule(),
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

    def to_tm_obj(self):
        return {
            "patterns": [fieldseq.to_tm_obj() for fieldseq in self.altfieldseq]
        }

class TmBaseSection:
    def __init__(self, config: TmConfig, name:str):
        self.name = name
        self.headers = TmAltFieldSequence(config, "headers-{}".format(name), [])
        self.rows = TmAltFieldSequence(config, "rows-{}".format(name), [])
    
    def add_header(self, fieldseq: TmFieldSequence):
        self.headers.add(fieldseq)
        return self
    
    def add_row(self, fieldseq: TmFieldSequence):
        self.rows.add(fieldseq)
        return self
    
    def to_tm_obj(self):
        return {
           "patterns": self.headers.to_tm_obj()["patterns"] + self.rows.to_tm_obj()["patterns"]
        }

class TextMateGrammar:
    def __init__(self, config: TmConfig):
        self.config: TmConfig = config
        self.sections: List[TmBaseSection] = [] 

    def add_section(self, section: TmBaseSection):
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
