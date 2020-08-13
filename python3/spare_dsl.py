from typing import List, Tuple, Dict, Set, Optional
from fractions import Fraction
from enum import Enum, auto
from dsl_text import SequenceConfig, SequencePersistence, RegExpConfig, RegExpPersistence, IntegerConfig, IntegerPersistence, BriefAnswer
from dsl_text import FloatConfig, FloatPersistence, FractionConfig, FractionPersistence, EnumConfig, EnumPersistence
from dsl_text import PersistenceSequence, PersistenceParserError



# Conversion

def id_to_nmo_str(value: str):
    return str(value)

def int_to_nmo_str(value: int):
    return str(value)

def float_to_nmo_str(value: float):
    return str(value)

def fraction_to_nmo_str(value: Fraction):
    return str(value)

def url_to_nmo_str(value: str):
    return str(value)

def email_to_nmo_str(value: str):
    return str(value)

def emails_to_nmo_str(emails: List[str]):
    return " ".join([email_to_nmo_str(email) for email in emails])

class ColorName(Enum):
    RED = auto()
    GREEN = auto()
    NOT_SUPPORTED = auto()
    
    @classmethod
    def from_nmo_string(cls, value: str):
        if value == "red":
            return ColorName.RED
        elif value == "green":
            return ColorName.GREEN
        else:
            return ColorName.NOT_SUPPORTED
    
    @classmethod
    def to_nmo_string(cls, value):
        if value == ColorName.RED:
            return "red"
        elif value == ColorName.GREEN:
            return "green"
        else:
            return "E"

class SpareItem:
    def __init__(self):
        self.v_float: float = -1.00
        self.v_fraction: Fraction = "1/1"

    def set_v_float(self, value: float):
            self.v_float = value
            return self

    def set_v_fraction(self, value: Fraction):
            self.v_fraction = value
            return self

    def to_string(self):
        return " ".join([
            "v_float", str(self.v_float),
            "v_fraction", str(self.v_fraction)
        ])

    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
            return self.to_string() == str(other)

    def to_nmo_string(self):
       return "v_float {} v_fraction {}".format(
            float_to_nmo_str(self.v_float),
            fraction_to_nmo_str(self.v_fraction)
            )


def items_to_nmo_str(items: List[SpareItem]):
    return " ".join([items.to_nmo_string() for item in items])


class SpareRow:
    def __init__(self):
        self.id:str = "no-id"
        self.v_int: int = -101
        self.url: str = "http://define.me"
        self.tags: Set[str] = set([])
        self.emails: List[str] = []
        self.color_name: ColorName = ColorName.NOT_SUPPORTED
        self.items: List[SpareItem] = []
        self.description: str = ""

    def set_v_int(self, value: int):
            self.v_int = value
            return self

    def set_url(self, value: str):
            self.url = value
            return self

    def set_tags(self, tags: Set[str]):
            self.tags = tags
            return self

    def add_tag(self, value: str):
        self.tags.add(value)
        return self

    def set_emails(self, emails: List[str]):
            self.emails = emails
            return self

    def add_email(self, value: str):
        self.emails.append(value)
        return self

    def set_color_name(self, value: ColorName):
        self.color_name = value
        return self

    def set_items(self, items: List[SpareItem]):
            self.items = items
            return self

    def add_item(self, value: SpareItem):
        self.items.append(value)
        return self

    def set_description(self, value: str):
            self.description = value
            return self

    def to_string(self):
        return " ".join([
        "id", self.id,
        "v_int", str(self.v_int),
        "url", self.url,
        "tags", str(self.tags),
        "emails", str(self.emails),
        "color_name", self.color_name.to_string(),
        "items", str(self.items),
        "description", str(self.items)
        ])

    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
            return self.to_string() == str(other)

    def to_nmo_string(self):
       return "id {} v_int {} url {} tags {} emails {} color_name {} items {} -> {}".format(
            id_to_nmo_str(self.id),
            int_to_nmo_str(self.v_int),
            url_to_nmo_str(self.url),
            str(self.tags),
            emails_to_nmo_str(self.emails),
            ColorName.to_nmo_string(self.color_name),
            str(self.items),
            str(self.description)
            )

# Persistence

class SpareItemParser:
    def __init__(self):
        self.marker1 = RegExpPersistence(RegExpConfig().set_name("marker1"))
        self.v_float= FloatPersistence(FloatConfig().set_name("v_float"))
        self.v_fraction= IntegerPersistence(FractionConfig().set_name("v_fraction"))

    def parse(self, chunk: str)->SpareItem:
        spareItem = SpareItem()
        trimmed = chunk.strip()
        if not self.marker1.satisfy(trimmed):
            raise PersistenceParserError("Expected {} but got {}".format("marker1", trimmed))
        return spareItem


class SpareRowParser:
    def __init__(self):
        self.id = RegExpPersistence(RegExpConfig().set_name("id"))
        self.v_int= IntegerPersistence(IntegerConfig().set_name("v_int"))
        self.url= RegExpPersistence(RegExpConfig().set_name("url"))
        self.tag = RegExpPersistence(RegExpConfig().set_name("tag"))
        self.tags = SequencePersistence(SequenceConfig().set_name("tags"))
        self.email = RegExpPersistence(RegExpConfig().set_name("email"))
        self.emails: SequencePersistence(SequenceConfig().set_name("emails"))
        self.color_name= EnumPersistence(EnumConfig().set_name("color_name"))
        self.item = SpareItemParser()
        self.items = SequencePersistence(SequenceConfig().set_name("items"))
        self.description = RegExpPersistence(RegExpConfig().set_name("description"))

    def parse(self, chunk: str)->SpareRow:
        spareRow = SpareRow()
        return spareRow
