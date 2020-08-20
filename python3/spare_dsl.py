from typing import List, Tuple, Dict, Set, Optional
from fractions import Fraction
from enum import Enum, auto
from dsl_text import SequenceConfig, SequencePersistence, RegExpConfig, RegExpPersistence, IntegerConfig, IntegerPersistence, BriefAnswer
from dsl_text import FloatConfig, FloatPersistence, FractionConfig, FractionPersistence, EnumConfig, EnumPersistence
from dsl_text import PersistenceSequence, PersistenceParserError, ParsingContext, BasePersistence



# Conversion

class SpareFormatter:
    def __init__(self):
        self.tags = SequencePersistence(SequenceConfig().set_name("tags").set_start("[").set_finish("]").set_separator(" "))
        self.emails = SequencePersistence(SequenceConfig().set_name("emails").set_start("[").set_finish("]").set_separator(" "))
        self.items = SequencePersistence(SequenceConfig().set_name("items").set_start("[").set_finish("]").set_separator(" "))

    def from_int(self, value: int)->str:
        return str(value)

    def from_float(self, value: float)->str:
        return str(value)

    def from_url(self, value: str)->str:
        return value.strip()

    def from_id(self, value: str)->str:
        return value.strip()

    def from_tag(self, value: str)->str:
        return value.strip()

    def from_email(self, value: str)->str:
        return value.strip()

    def from_fraction(self, value: Fraction)->str:
        return str(value)

    def from_tags(self, values: List[str])->str:
        return self.tags.to_csv_string([self.from_tag(value) for value in values])

    def from_emails(self, values: List[str])->str:
        return self.emails.to_csv_string([self.from_email(value) for value in values])

    def from_items(self, values: List[str])->str:
        return self.items.to_csv_string(values)


sf =  SpareFormatter()

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

    def set_v_float_as_str(self, value: str):
        return self.set_v_float(float(value))

    def set_v_fraction(self, value: Fraction):
            self.v_fraction = value
            return self
    
    def set_v_fraction_as_str(self, value: str):
            return self.set_v_fraction(Fraction(value))

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
            sf.from_float(self.v_float),
            sf.from_fraction(self.v_fraction)
            )


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

    def set_id(self, value: str):
            self.id = value
            return self

    def set_v_int(self, value: int):
            self.v_int = value
            return self
    
    def set_v_int_as_str(self, value: str):
        return self.set_v_int(int(value))

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

    def set_color_name_as_str(self, value: str):
        return self.set_color_name(ColorName.from_nmo_string(value))

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
       return "row {} {} {} tags {} emails {} {} items {} -> {}".format(
            sf.from_id(self.id),
            sf.from_fraction(self.v_int),
            sf.from_url(self.url),
            sf.from_tags(self.tags),
            sf.from_emails(self.emails),
            ColorName.to_nmo_string(self.color_name),
            sf.from_items([item.to_nmo_string() for item in self.items]),
            self.description
            )


# Persistence

class SpareItemParser:
    def __init__(self):
        self.marker1 = RegExpPersistence(RegExpConfig().set_name("marker1"))
        self.v_float= FloatPersistence(FloatConfig().set_name("v_float"))
        self.v_fraction= IntegerPersistence(FractionConfig().set_name("v_fraction"))

    def parse(self, ctx: ParsingContext, chunk: str)->SpareItem:
        after_marker1 = self.marker1.consume_marker(ctx, chunk)
        (value_v_float, after_v_float) = self.v_float.parse_ctx_string(ctx, after_marker1)
        (value_v_fraction, _) = self.v_fraction.parse_ctx_string(ctx, after_v_float)

        spareItem = SpareItem()
        spareItem.set_v_float_as_str(value_v_float)
        spareItem.set_v_fraction_as_str(value_v_fraction)
        return spareItem


class SpareRowParser:
    def __init__(self):
        self.marker_row = RegExpPersistence(RegExpConfig().set_name("marker_row").set_match("row"))
        self.id = RegExpPersistence(RegExpConfig().set_name("id").set_match(r"[a-z0-9_-]+"))
        self.v_int= IntegerPersistence(IntegerConfig().set_name("v_int"))
        self.url= RegExpPersistence(RegExpConfig().set_name("url").set_match(r"https?://[A-Za-z0-9/_.-]+"))
        self.tag = RegExpPersistence(RegExpConfig().set_name("tag"))
        self.marker_tags = RegExpPersistence(RegExpConfig().set_name("marker_tags").set_match("tags"))
        self.tags = SequencePersistence(SequenceConfig().set_name("tags"))
        self.email = RegExpPersistence(RegExpConfig().set_name("email"))
        self.marker_emails = RegExpPersistence(RegExpConfig().set_name("marker_emails").set_match("emails"))
        self.emails = SequencePersistence(SequenceConfig().set_name("emails"))
        self.color_name= EnumPersistence(EnumConfig().set_name("color_name"))
        self.item = SpareItemParser()
        self.items = SequencePersistence(SequenceConfig().set_name("items"))
        self.description = RegExpPersistence(RegExpConfig().set_name("description"))

    def parse(self, ctx: ParsingContext, chunk: str)->SpareRow:
        after_marker_row = self.marker_row.consume_marker(ctx, chunk)
        (id, after_id) = self.id.parse_ctx_string(ctx, after_marker_row)
        (v_int, after_v_int) = self.v_int.parse_ctx_string(ctx, after_id)
        (url, after_url) = self.url.parse_ctx_string(ctx, after_v_int)
        after_marker_tags = self.marker_tags.consume_marker(ctx, after_url)
        (tag_strlist, after_tags) = self.tags.parse_ctx_list(ctx, after_marker_tags)
        self.tag.list_satisfy_ctx(ctx, tag_strlist)
        tags = set(self.tag.list_parse_string_ctx(ctx, tag_strlist))
        after_emails_marker = self.marker_emails.consume_marker(ctx, after_tags)
        (email_strlist, after_emails) = self.emails.parse_ctx_list(ctx, after_emails_marker)
        self.email.list_satisfy_ctx(ctx, email_strlist)
        emails = self.email.list_parse_string_ctx(ctx, email_strlist)
        (color_name, after_color_name) = self.url.parse_ctx_string(ctx, after_emails)
        (items_strlist, _) = self.items.parse_ctx_list(ctx, after_color_name)
        items = [self.item.parse(ctx, item) for item in items_strlist]
        spareRow = SpareRow()
        spareRow.set_id(id)
        spareRow.set_v_int_as_str(v_int)
        spareRow.set_url(url)
        spareRow.set_tags(tags)
        spareRow.set_emails(emails)
        spareRow.set_color_name_as_str(color_name)
        spareRow.set_items(items)
        return spareRow
