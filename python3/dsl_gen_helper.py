from typing import List, Tuple, Dict, Set, Optional, Union
import re

non_alpha_pattern = re.compile("[^A-Za-z0-9]+")
def to_constant_str(value: str)->str:
    return non_alpha_pattern.sub(value, "_").upper()


class GenBase:
    def get_name(self)->str:
        pass

class GenEnumConfig(GenBase):
    def __init__(self):
        self.name = "no-name"
        self.values: List[str] = []

    def set_name(self, name: str):
        self.name = name
        return self

    def set_values(self, values: List[str]):
        self.values = values
        return self

    def get_values_as_const(self)->List[str]:
        return map(to_constant_str, self.values)


    