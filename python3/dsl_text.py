from typing import List, Tuple, Dict, Set

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

def discard_empty(lines):
    return [line.strip() for line in lines if len(line.strip())>0]

class SequenceManager:
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
    
    def _strip_string_array(self, line: str)->List[str]:
        return [separated.strip() for separated in line.split(self.separator) if separated.strip() != ""]

    def parse_as_list(self, line:str)->List[str]:
        return self._strip_string_array(line)

    def expect_list(self, line: str)->(str, str):
        trimmed = line.strip()
        if len(trimmed) == 0:
            return ("", "")
        if (trimmed[0] != self.start):
            return ("", trimmed)
        finished = line.find(self.finish)
        if (finished < 0):
            return ("", trimmed)
        return (trimmed[1:finished], trimmed[finished:])

        