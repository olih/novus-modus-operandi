from typing import List, Tuple, Dict, Set, Optional
from fractions import Fraction
from enum import Enum, auto
from dsl_text import SequenceConfig, SequencePersistence, RegExpConfig, RegExpPersistence, IntegerConfig, IntegerPersistence, BriefAnswer
from dsl_text import FloatConfig, FloatPersistence, FractionConfig, FractionPersistence, EnumConfig, EnumPersistence
from dsl_text import PersistenceSequence, PersistenceParserError, ParsingContext



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

    def parse(self, ctx: ParsingContext, chunk: str)->SpareItem:
        if not self.marker1.satisfy(chunk):
            raise PersistenceParserError(ctx, "marker1", chunk)
        (_, after_marker1) = self.marker1.parse_as_string(chunk)
        if not self.v_float.satisfy(after_marker1):
            raise PersistenceParserError(ctx, "v_float", after_marker1)
        (value_v_float, after_v_float) = self.v_float.parse_as_string(after_marker1)
        if not self.v_fraction.satisfy(after_v_float):
            raise PersistenceParserError(ctx, "v_fraction", after_v_float)
        (value_v_fraction, _) = self.v_fraction.parse_as_string(after_v_float)

        spareItem = SpareItem()
        spareItem.set_v_float_as_str(value_v_float)
        spareItem.set_v_fraction_as_str(value_v_fraction)
        return spareItem


class SpareRowParser:
    def __init__(self):
        self.marker_row = RegExpPersistence(RegExpConfig().set_name("marker_row").set_match("row"))
        self.id = RegExpPersistence(RegExpConfig().set_name("id").set_match(r"[a-z0-9_-]"))
        self.v_int= IntegerPersistence(IntegerConfig().set_name("v_int"))
        self.url= RegExpPersistence(RegExpConfig().set_name("url").set_match(r"https?://[A-Za-z0-9/_.-]+"))
        self.tag = RegExpPersistence(RegExpConfig().set_name("tag"))
        self.marker_tags = RegExpPersistence(RegExpConfig().set_name("marker_tags").set_match("tags"))
        self.tags = SequencePersistence(SequenceConfig().set_name("tags"))
        self.email = RegExpPersistence(RegExpConfig().set_name("email"))
        self.emails: SequencePersistence(SequenceConfig().set_name("emails"))
        self.color_name= EnumPersistence(EnumConfig().set_name("color_name"))
        self.item = SpareItemParser()
        self.items = SequencePersistence(SequenceConfig().set_name("items"))
        self.description = RegExpPersistence(RegExpConfig().set_name("description"))

    def parse(self, ctx: ParsingContext, chunk: str)->SpareRow:
        if not self.marker_row.satisfy(chunk):
            raise PersistenceParserError(ctx, "marker_row", chunk)
        (_, after_marker_row) = self.marker_row.parse_as_string(chunk)
        if not self.id.satisfy(after_marker_row):
            raise PersistenceParserError(ctx, "id", after_marker_row)
        (id, after_id) = self.id.parse_as_string(after_marker_row)
        if not self.v_int.satisfy(after_id):
            raise PersistenceParserError(ctx, "v_int", after_id)
        (v_int, after_v_int) = self.v_int.parse_as_string(after_marker_row)
        if not self.url.satisfy(after_v_int):
            raise PersistenceParserError(ctx, "url", after_v_int)
        (url, after_url) = self.url.parse_as_string(after_v_int)
        if not self.marker_tags.satisfy(after_url):
            raise PersistenceParserError(ctx, "marker_tags", after_url)
        (_, after_marker_tags) = self.marker_tags.parse_as_string(after_url)
        if not self.tags.satisfy(after_marker_tags):
            raise PersistenceParserError(ctx, "tags", after_marker_tags)
        (tag_strlist, after_tags) = self.tags.parse_as_list(after_marker_tags)
        for tag in tag_strlist:
            if not self.tag.satisfy(tag):
                raise PersistenceParserError(ctx, "tag", tag)
        tags = set([self.tag.parse_as_string(tag)[0] for tag in tag_strlist])
        if not self.emails.satisfy(after_tags):
            raise PersistenceParserError(ctx, "emails", after_tags)
        (email_strlist, after_emails) = self.emails.parse_as_list(after_tags)
        for email in email_strlist:
            if not self.email.satisfy(email):
                raise PersistenceParserError(ctx, "email", email)
        emails = [self.email.parse_as_string(email)[0] for email in email_strlist]
        if not self.color_name.satisfy(after_emails):
            raise PersistenceParserError(ctx, "color_name", after_emails)
        (color_name, after_color_name) = self.url.parse_as_string(after_emails)
        if not self.items.satisfy(after_color_name):
            raise PersistenceParserError(ctx, "items", after_color_name)
        (items_strlist, _) = self.items.parse_as_list(after_color_name)
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
