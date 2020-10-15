from typing import List, Tuple, Dict, Set, Optional, Union
import re

non_alpha_pattern = re.compile("[^A-Za-z0-9]+")

def to_constant_str(value: str)->str:
    return non_alpha_pattern.sub(value, "_").upper()

def to_const_and_value(value: str)->Tuple[str]:
    return (to_constant_str(value), value)

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
    
    def get_values_as_const_and_val(self)->List[Tuple[str]]:
        return map(to_const_and_value, self.values)


standard_types = ["str", "int", "float", "Fraction"]

class ValueObj:
    def __init__(self, name: str, value_type: str, default_value: str):
        self.name = name
        self.value_type = value_type
        self.default_value = default_value
        self.is_list = self.value_type.startswith("List[")
        self.is_set = self.value_type.startswith("Set[")
        self.core_value_type = value_type.replace("List[", "").replace("Set[", "").replace("]", "")
        self.is_standard_type = self.core_value_type in standard_types
     

class GenValueObjConfig(GenBase):
    def __init__(self):
        self.name = "no-name"
        self.values: List[ValueObj] = []

    def set_name(self, name: str):
        self.name = name
        return self

    def set_values(self, values: List[ValueObj]):
        self.values = values
        return self
    