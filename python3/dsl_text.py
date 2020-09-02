from typing import List, Tuple, Dict, Set, Optional, Union
import re
from enum import Enum, auto
from fractions import Fraction

def discard_empty(lines):
    return [line.strip() for line in lines if len(line.strip())>0]

class ParsingContext:
    def __init__(self):
        self.id = "no-id"
        self.line_number = 0
    
    def set_id(self, id: str):
        self.id = id
        return self

    def set_line_number(self, line_number: int):
        self.line_number = line_number
        return self

    def to_string(self):
        return "Id: {} Ln: {}".format(self.id, self.line_number)

    def __str__(self):
        return self.to_string()

class PersistenceParserError(Exception):
    """Raised when the input cannot be parsed"""
    def __init__(self, context: ParsingContext, name: str, actual: str):
        message = "Expected {} for {} but got {}".format(name, context, actual)
        super().__init__(message)

class BasePersistence:
    def get_name(self)->str:
        pass

    def satisfy(self, strchunk: str)->bool:
        pass
    
    def parse_as_string(self, strchunk: str)->(str, str):
        pass

    def parse_as_list(self, strchunk: str)->(List[str], str):
        pass
     
    def to_csv_string(self, values: List[str])->str:
        pass

    def consume_marker(self, ctx: ParsingContext, strchunk: str):
        if not self.satisfy(strchunk):
            raise PersistenceParserError(ctx, self.get_name(), strchunk)
        self.parse_as_string(strchunk)
        return self.parse_as_string(strchunk)[1]

    def parse_ctx_string(self, ctx: ParsingContext, strchunk: str)->(str, str):
        if not self.satisfy(strchunk):
                raise PersistenceParserError(ctx, self.get_name(), strchunk)
        return self.parse_as_string(strchunk)

    def parse_ctx_list(self, ctx: ParsingContext, strchunk: str)->(List[str], str):
        if not self.satisfy(strchunk):
                raise PersistenceParserError(ctx, self.get_name(), strchunk)
        return self.parse_as_list(strchunk)

    def list_satisfy_ctx(self, ctx: ParsingContext, chunks: List[str]):
        for chunk in chunks:
            if not self.satisfy(chunk):
                raise PersistenceParserError(ctx, self.get_name(), chunk)

    def list_parse_string_ctx(self, ctx: ParsingContext, chunks: List[str])->List[str]:
        return [self.parse_ctx_string(ctx, chunk)[0] for chunk in chunks]
            

class PersistenceContainer:    
    def todo(self)->bool:
        return True

class PersistenceSequence(PersistenceContainer):
    def __init__(self, persistences: List[Union[BasePersistence, PersistenceContainer]]):
        super().__init__()
        self.persistences = persistences
             
class PersistenceAlternatives(PersistenceContainer):
    def __init__(self, persistences: List[Union[BasePersistence, PersistenceContainer]]):
        super().__init__()
        self.persistences = persistences

class SequenceConfig:
    def __init__(self):
        self.name = "seq-no-name"
        self.start = "["
        self.finish = "]"
        self.separator = ","
        self.container = PersistenceAlternatives([])

    def set_name(self, name: str):
        self.name = name
        return self

    def set_start(self, start: str):
        self.start = start
        return self

    def set_finish(self, finish: str):
        self.finish = finish
        return self

    def set_separator(self, separator: str):
        self.separator = separator
        return self

    def set_container(self, container: PersistenceContainer):
        self.container = container
        return self

class SequencePersistence(BasePersistence):
    def __init__(self, cfg: SequenceConfig):
        self.cfg = cfg

    def get_name(self)->str:
        return self.cfg.name

    def _strip_string_array(self, line: str)->List[str]:
        return [separated.strip() for separated in line.split(self.cfg.separator) if separated.strip() != ""]

    def satisfy(self, strchunk: str)->bool:
        trimmed = strchunk.strip()
        if len(trimmed) < 2:
            return False
        if (trimmed[0] != self.cfg.start):
            return False
        finished = trimmed.find(self.cfg.finish)
        if (finished < 0):
            return False
        return True

    def parse_as_string(self, strchunk: str)->(str, str):
        satisfied = self.satisfy(strchunk)
        if not satisfied:
            raise Exception("Chunk cannot be parsed: {}".format(strchunk)) # Should never happen if we check first
        trimmed = strchunk.strip()
        finished = trimmed.find(self.cfg.finish)
        return (trimmed[1:finished], trimmed[finished+1:])

    def parse_as_list(self, strchunk: str)->(List[str], str):
        (extracted, remain) = self.parse_as_string(strchunk)
        return (self._strip_string_array(extracted),remain)

    def to_csv_string(self, values: List[str])->str:
         return "{} {} {}".format(self.cfg.start, self.cfg.separator.join(values), self.cfg.finish)


class RegExpConfig:
    def __init__(self):
        self.name = "regex-no-name"
        self.match = ".*"
        self.pattern = re.compile(".*")
        self.separator = " "

    def set_name(self, name: str):
        self.name = name
        return self

    def set_match(self, match: str):
        self.match = match
        self.pattern = re.compile(match)
        return self

    def set_separator(self, separator: str):
        self.separator = separator
        return self

    def match_str(self, chunk: str):
        return self.pattern.match(chunk)

class RegExpPersistence(BasePersistence):
    def __init__(self, cfg: RegExpConfig):
        self.cfg = cfg
    
    def get_name(self)->str:
        return self.cfg.name
   
    def satisfy(self, strchunk: str)->bool:
        trimmed = strchunk.strip()
        finished = trimmed.find(self.cfg.separator)
        candidate = trimmed if finished < 0 else trimmed[:finished]
        return self.cfg.match_str(candidate) != None

    
    def parse_as_string(self, strchunk: str)->(str, str):
        satisfied = self.satisfy(strchunk)
        if not satisfied:
            raise Exception("Chunk cannot be parsed: {}".format(strchunk)) # Should never happen if we check first
        trimmed = strchunk.strip()
        finished = trimmed.find(self.cfg.separator)
        candidate = (trimmed, "") if finished < 0 else (trimmed[:finished], trimmed[finished+1:])
        return candidate

    def parse_as_list(self, strchunk: str)->(List[str], str):
        raise Exception("Not supported for RegExpPersistence")
     
    def to_csv_string(self, values: List[str])->str:
        return "".join(values)

class BriefAnswer(Enum):
   Yes = auto()
   No = auto()
   Maybe = auto()

class IntegerConfig:
    def __init__(self):
        self.name = "int-no-name"
        self.has_sign = BriefAnswer.Maybe
        self.separator = " "
        self.pattern = re.compile(r"^(\+|-)?[0-9]+")

    def set_name(self, name: str):
        self.name = name
        return self

    def set_has_sign(self, has_sign: BriefAnswer):
        self.has_sign = has_sign
        return self

    def set_separator(self, separator: str):
        self.separator = separator
        return self

    def match_str(self, chunk: str):
        return self.pattern.match(chunk)

class IntegerPersistence(BasePersistence):
    def __init__(self, cfg: IntegerConfig):
        self.cfg = cfg

    def get_name(self)->str:
        return self.cfg.name

    def satisfy(self, strchunk: str)->bool:
        trimmed = strchunk.lstrip()
        finished = trimmed.find(self.cfg.separator)
        candidate = trimmed if finished < 0 else trimmed[:finished]
        if self.cfg.match_str(candidate) == None:
            return False
        if candidate == "0":
            return True
        if (candidate[0] == "+" or candidate[0] == "-") and self.cfg.has_sign == BriefAnswer.No:
            return False
        if not (candidate[0] == "+" or candidate[0] == "-") and self.cfg.has_sign == BriefAnswer.Yes:
            return False
        try:
            int(candidate)
            return True
        except:
            return False
    
    def parse_as_string(self, strchunk: str)->(str, str):
        satisfied = self.satisfy(strchunk)
        if not satisfied:
            raise Exception("Chunk cannot be parsed: {}".format(strchunk)) # Should never happen if we check first
        trimmed = strchunk.strip()
        finished = trimmed.find(self.cfg.separator)
        candidate = (trimmed, "") if finished < 0 else (trimmed[:finished], trimmed[finished+1:])
        return candidate

    def parse_as_list(self, strchunk: str)->(List[str], str):
        raise Exception("Not supported for IntegerPersistence")
     
    def to_csv_string(self, values: List[str])->str:
        return "".join(values)

class FloatConfig:
    def __init__(self):
        self.name = "float-no-name"
        self.has_sign = BriefAnswer.Maybe
        self.separator = " "
        self.pattern = re.compile(r"^(\+|-)?[0-9.]+")
    
    def set_name(self, name: str):
        self.name = name
        return self

    def set_has_sign(self, has_sign: BriefAnswer):
        self.has_sign = has_sign
        return self

    def set_separator(self, separator: str):
        self.separator = separator
        return self

    def match_str(self, chunk: str):
        return self.pattern.match(chunk)

class FloatPersistence(BasePersistence):
    def __init__(self, cfg: FloatConfig):
        self.cfg = cfg

    def get_name(self)->str:
        return self.cfg.name

    def satisfy(self, strchunk: str)->bool:
        trimmed = strchunk.lstrip()
        finished = trimmed.find(self.cfg.separator)
        candidate = trimmed if finished < 0 else trimmed[:finished]
        if self.cfg.match_str(candidate) == None:
            return False
        if candidate == "0":
            return True
        if (candidate[0] == "+" or candidate[0] == "-") and self.cfg.has_sign == BriefAnswer.No:
            return False
        if not (candidate[0] == "+" or candidate[0] == "-") and self.cfg.has_sign == BriefAnswer.Yes:
            return False
        try:
            float(candidate)
            return True
        except:
            return False
    
    def parse_as_string(self, strchunk: str)->(str, str):
        satisfied = self.satisfy(strchunk)
        if not satisfied:
            raise Exception("Chunk cannot be parsed: {}".format(strchunk)) # Should never happen if we check first
        trimmed = strchunk.strip()
        finished = trimmed.find(self.cfg.separator)
        candidate = (trimmed, "") if finished < 0 else (trimmed[:finished], trimmed[finished+1:])
        return candidate

    def parse_as_list(self, strchunk: str)->(List[str], str):
        raise Exception("Not supported for FloatPersistence")
     
    def to_csv_string(self, values: List[str])->str:
        return "".join(values)

class FractionConfig:
    def __init__(self):
        self.name = "fraction-no-name"
        self.has_sign = BriefAnswer.Maybe
        self.separator = " "
        self.pattern = re.compile(r"^(\+|-)?(?:[1-9][0-9]*|0)(?:\/[1-9][0-9]*)?$")
    
    def set_name(self, name: str):
        self.name = name
        return self

    def set_has_sign(self, has_sign: BriefAnswer):
        self.has_sign = has_sign
        return self

    def set_separator(self, separator: str):
        self.separator = separator
        return self

    def match_str(self, chunk: str):
        return self.pattern.match(chunk)

class FractionPersistence(BasePersistence):
    def __init__(self, cfg: FractionConfig):
        self.cfg = cfg

    def get_name(self)->str:
        return self.cfg.name

    def satisfy(self, strchunk: str)->bool:
        trimmed = strchunk.lstrip()
        finished = trimmed.find(self.cfg.separator)
        candidate = trimmed if finished < 0 else trimmed[:finished]
        if self.cfg.match_str(candidate) == None:
            return False
        if candidate == "0":
            return True
        if (candidate[0] == "+" or candidate[0] == "-") and self.cfg.has_sign == BriefAnswer.No:
            return False
        if not (candidate[0] == "+" or candidate[0] == "-") and self.cfg.has_sign == BriefAnswer.Yes:
            return False
        try:
            Fraction(candidate)
            return True
        except:
            return False
    
    def parse_as_string(self, strchunk: str)->(str, str):
        satisfied = self.satisfy(strchunk)
        if not satisfied:
            raise Exception("Chunk cannot be parsed: {}".format(strchunk)) # Should never happen if we check first
        trimmed = strchunk.strip()
        finished = trimmed.find(self.cfg.separator)
        candidate = (trimmed, "") if finished < 0 else (trimmed[:finished], trimmed[finished+1:])
        return candidate

    def parse_as_list(self, strchunk: str)->(List[str], str):
        raise Exception("Not supported for FractionPersistence")
     
    def to_csv_string(self, values: List[str])->str:
        return "".join(values)

class EnumConfig:
    def __init__(self):
        self.name = "enum-no-name"
        self.values = []
        self.separator = " "
    
    def set_name(self, name: str):
        self.name = name
        return self

    def set_separator(self, separator: str):
        self.separator = separator
        return self

    def set_values(self, values: List[str]):
        self.values = values
        return self

    def match_str(self, chunk: str):
        return chunk in self.values

class EnumPersistence(BasePersistence):
    def __init__(self, cfg: EnumConfig):
        self.cfg = cfg

    def get_name(self)->str:
        return self.cfg.name

    def satisfy(self, strchunk: str)->bool:
        trimmed = strchunk.strip()
        finished = trimmed.find(self.cfg.separator)
        candidate = trimmed if finished < 0 else trimmed[:finished]
        return self.cfg.match_str(candidate)
    
    def parse_as_string(self, strchunk: str)->(str, str):
        satisfied = self.satisfy(strchunk)
        if not satisfied:
            raise Exception("Chunk cannot be parsed: {}".format(strchunk)) # Should never happen if we check first
        trimmed = strchunk.strip()
        finished = trimmed.find(self.cfg.separator)
        candidate = (trimmed, "") if finished < 0 else (trimmed[:finished], trimmed[finished+1:])
        return candidate

    def parse_as_list(self, strchunk: str)->(List[str], str):
        raise Exception("Not supported for EnumPersistence")
     
    def to_csv_string(self, values: List[str])->str:
        return "".join(values)


def match_field(expected: str, actual: str)->bool:
    if expected == "*":
        return True
    return expected == actual

class RowDetectorOption:
    def __init__(self):
        self.name = "no-name"
        self.prefixes = []
        self.separator = " "

    def set_name(self, name: str):
        self.name = name
        return self
   
    def set_prefixes(self, values: List[str]):
        self.prefixes = values
        return self
    
    def set_separator(self, separator: str):
        self.separator = separator
        return self

    def match(self, line: str)->bool:
        parts = line.split(self.separator)
        try:
            results = set([match_field(self.prefixes[i],parts[i]) for i in range(len(self.prefixes))])
            return not (False in results)
        except IndexError:
            return False

class RowDetector:
    def __init__(self):
        self.options = []

    def set_options(self, options: List[RowDetectorOption]):
        self.options = options
        self._sort_options()
        return self

    def add_option(self, option: RowDetectorOption):
        self.options.append(option)
        self._sort_options()
        return self

    def _sort_options(self):
        self.options = sorted(self.options, key = lambda option: len(option.prefixes), reverse=True)

    def match(self, line: str)->Optional[str]:
        for option in self.options:
            if option.match(line):
                return option.name
        return None

class LineParser:
    def parse(self, ctx: ParsingContext, chunk: str):
        pass

class LineParserConfig:
    def __init__(self):
        self.name = "enum-no-name"
        self.single = False

    def set_name(self, name: str):
        self.name = name
        return self

    def set_parser(self, parser: LineParser):
        self.parser = parser
        return self

    def set_single(self):
        self.single = True
        return self
    
    def set_multiple(self):
        self.single = False
        return self

class ScriptParser:
    def __init__(self):
        self.line_parser_configs = {}

    def add_line_parser_cfg(self, line_parser_cfg: LineParserConfig):
        self.line_parser_configs[line_parser_cfg.name] = line_parser_cfg
        return self