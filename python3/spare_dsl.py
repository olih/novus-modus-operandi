from typing import List, Tuple, Dict, Set
from fractions import Fraction
from enum import Enum, auto

class ColorName(Enum):
    RED = auto()
    GREEN = auto()
    NOT_SUPPORTED = auto()
    
    @classmethod
    def from_string(cls, value: str):
        if value == "red":
            return ColorName.RED
        elif value == "green":
            return ColorName.GREEN
        else:
            return ColorName.NOT_SUPPORTED
    
    @classmethod
    def to_string(cls, value):
        if value == ColorName.RED:
            return "red"
        elif value == ColorName.GREEN:
            return "green"
        else:
            return "E"

class SpareRow:
    def __init__(self, id: str):
        self.id = id
        self.v_int = -101
        self.url = "http://define.me"
        self.tags = []
        self.color_name = ColorName.NOT_SUPPORTED

    def set_v_int(self, value: int):
            self.v_int = value
            return self

    def set_url(self, value: str):
            self.url = value
            return self

    def set_tags(self, tags: List[str]):
            self.tags = tags
            return self

    def add_tag(self, value: str):
        self.tags.append(value)
        return self

    def set_color_name(self, value: ColorName):
        self.color_name = value
        return self