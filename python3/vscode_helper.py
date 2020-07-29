from typing import List, Tuple, Dict, Set

def escape_re(value: str)->str:
    return value

def paren(value: str)->str:
    return "({})".format(value)

class TmConfig:
    def __init__(self):
        self.extname

    def set_extension(self, extname: str):
        self.extname = extname
        return self

class TmBaseField:
    def to_tm_ob(self):
        pass

    def singleton(self):
        return [self]


class TmSimpleRegexField(TmBaseField):
    def __init__(self, config: TmConfig, name: str, scope: str, match: str):
        self.config = config
        self.name = name
        self.match = match
        self.scope = scope

    def to_tm_ob(self):
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

    def to_tm_ob(self):
        return {
            "comment": "{}".format(self.name),
            "match": "|".join(sorted(list(set([escape_re(k.strip()) for k in self.keywords])))),
            "name": "{}.{}".format(self.scope, self.config.extname)
        }

class TmFieldSequence(TmBaseField):
    def __init__(self, config: TmConfig, name: str, start: str, finish: str, fieldseq: List[TmBaseField]) :
        self.name = name
        self.fieldseq = fieldseq
        self.start = start
        self.finish = finish
    
    def _to_match_rule(self)->str:
        match_seq = "[ ]*".join([paren(field.to_tm_ob().match) for field in self.fieldseq])
        match = "{}{}{}".format(escape_re(self.start), match_seq, escape_re(self.finish))
        return match

    def _to_captures_rule(self):
        result = {}
        count = 0
        for field in self.fieldseq:
            count = count + 1
            result[str(count)] = field.to_tm_ob()
        return result
    
    def _to_comment(self)->str:
        comment = " ".join([field.to_tm_ob().comment for field in self.fieldseq])
        return comment

    def to_tm_ob(self):
        return {
            "comment": self._to_comment(),
            "match": self._to_match_rule(),
            "captures" : self._to_captures_rule(),
        }
    
    def singleton(self):
        return [self]

class TmAltFieldSequence(TmBaseField):
    def __init__(self, config: TmConfig, name: str, start: str, finish: str, altfieldseq: List[TmFieldSequence]) :
        self.name = name
        self.altfieldseq = altfieldseq
        self.start = start
        self.finish = finish

    def to_tm_ob(self):
        return {
            "patterns": [fieldseq.to_tm_ob() for fieldseq in self.altfieldseq]
        }
