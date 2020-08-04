from typing import List, Tuple, Dict, Set, Optional
import re

def discard_empty(lines):
    return [line.strip() for line in lines if len(line.strip())>0]

class BasePersistence:
    def satisfy(self, strchunk: str)->bool:
        pass
    
    def parse_as_string(self, strchunk: str)->(str, str):
        pass

    def parse_as_list(self, strchunk: str)->(List[str], str):
        pass
     
    def to_csv_string(self, values: List[str])->str:
        pass

class SequenceConfig:
    def __init__(self):
        self.start = "["
        self.finish = "]"
        self.separator = ","

    def set_start(self, start: str):
        self.start = start
        return self

    def set_finish(self, finish: str):
        self.finish = finish
        return self

    def set_separator(self, separator: str):
        self.separator = separator
        return self

class SequencePersistence(BasePersistence):
    def __init__(self, cfg: SequenceConfig):
        self.cfg = cfg
    
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
        self.match = ".*"
        self.pattern = re.compile(".*")
        self.separator = " "

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
   
    def satisfy(self, strchunk: str)->bool:
        trimmed = strchunk.strip()
        finished = trimmed.find(self.cfg.separator)
        candidate = trimmed if finished < 0 else trimmed[:finished]
        return self.cfg.match_str(candidate) is not None

    
    def parse_as_string(self, strchunk: str)->(str, str):
        pass

    def parse_as_list(self, strchunk: str)->(List[str], str):
        pass
     
    def to_csv_string(self, values: List[str])->str:
        pass

