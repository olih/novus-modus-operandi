from typing import List, Tuple, Dict, Set, Optional
from fractions import Fraction
from enum import Enum, auto
from dsl_text import SequenceConfig, SequencePersistence, RegExpConfig, RegExpPersistence, IntegerConfig, IntegerPersistence, BriefAnswer
from dsl_text import FloatConfig, FloatPersistence, FractionConfig, FractionPersistence, EnumConfig, EnumPersistence
from dsl_text import PersistenceSequence, PersistenceParserError, ParsingContext, BasePersistence
from dsl_text import RowDetectorOption, RowDetector, LineParser, LineParserConfig, ScriptParser

# Conversion

class SpareFormatter:
    def __init__(self):
        self.tags = SequencePersistence(SequenceConfig().set_name("tags").set_start("[").set_finish("]").set_separator(" "))
        self.emails = SequencePersistence(SequenceConfig().set_name("emails").set_start("[").set_finish("]").set_separator(" "))
        self.items = SequencePersistence(SequenceConfig().set_name("items").set_start("[").set_finish("]").set_separator(","))

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

class SpareSectionType(Enum):
    ALPHA = auto()
    BETA = auto()
    NOT_SUPPORTED = auto()
    
    @classmethod
    def from_nmo_string(cls, value: str):
        if value == "alpha":
            return SpareSectionType.ALPHA
        elif value == "beta":
            return SpareSectionType.BETA
        else:
            return SpareSectionType.NOT_SUPPORTED
    
    @classmethod
    def to_nmo_string(cls, value):
        if value == SpareSectionType.ALPHA:
            return "alpha"
        elif value == SpareSectionType.BETA:
            return "beta"
        else:
            return "E"


class SpareSection:
    def __init__(self):
        self.section_type: SpareSectionType = SpareSectionType.NOT_SUPPORTED

    def set_section_type(self, value: SpareSectionType):
            self.section_type = value
            return self

    def set_section_type_as_str(self, value: str):
        return self.set_section_type(SpareSectionType.from_nmo_string(value))

    def to_string(self):
        return " ".join([
            "section_type", str(self.section_type)
        ])
    
    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
            return self.to_string() == str(other)

    def to_nmo_string(self):
       return "section {}".format(
            SpareSectionType.to_nmo_string(self.section_type),
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
        "color_name", str(self.color_name),
        "items", str(self.items),
        "description", str(self.description)
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

class SpareItemParser(LineParser):
    def __init__(self):
        self.marker_v_float = RegExpPersistence(RegExpConfig().set_name("marker_v_float").set_match("v_float"))
        self.v_float= FloatPersistence(FloatConfig().set_name("v_float"))
        self.marker_v_fraction = RegExpPersistence(RegExpConfig().set_name("marker_v_fraction").set_match("v_fraction"))
        self.v_fraction= FractionPersistence(FractionConfig().set_name("v_fraction"))

    def parse(self, ctx: ParsingContext, chunk: str)->SpareItem:
        after_marker_v_float = self.marker_v_float.consume_marker(ctx, chunk)
        (value_v_float, after_v_float) = self.v_float.parse_ctx_string(ctx, after_marker_v_float)
        after_marker_v_fraction = self.marker_v_fraction.consume_marker(ctx, after_v_float)
        (value_v_fraction, _) = self.v_fraction.parse_ctx_string(ctx, after_marker_v_fraction)

        spareItem = SpareItem()
        spareItem.set_v_float_as_str(value_v_float)
        spareItem.set_v_fraction_as_str(value_v_fraction)
        return spareItem


class SpareRowParser(LineParser):
    def __init__(self):
        self.marker_row = RegExpPersistence(RegExpConfig().set_name("marker_row").set_match("row"))
        self.id = RegExpPersistence(RegExpConfig().set_name("id").set_match(r"[a-z0-9_-]+"))
        self.v_int= IntegerPersistence(IntegerConfig().set_name("v_int"))
        self.url= RegExpPersistence(RegExpConfig().set_name("url").set_match(r"https?://[A-Za-z0-9/_.-]+"))
        self.tag = RegExpPersistence(RegExpConfig().set_name("tag"))
        self.marker_tags = RegExpPersistence(RegExpConfig().set_name("marker_tags").set_match("tags"))
        self.tags = SequencePersistence(SequenceConfig().set_name("tags").set_start("[").set_finish("]").set_separator(" "))
        self.email = RegExpPersistence(RegExpConfig().set_name("email"))
        self.marker_emails = RegExpPersistence(RegExpConfig().set_name("marker_emails").set_match("emails"))
        self.emails = SequencePersistence(SequenceConfig().set_name("emails").set_start("[").set_finish("]").set_separator(" "))
        self.color_name= EnumPersistence(EnumConfig().set_name("color_name").set_values(["green", "orange", "red"]))
        self.item = SpareItemParser()
        self.marker_items = RegExpPersistence(RegExpConfig().set_name("marker_items").set_match("items"))
        self.items = SequencePersistence(SequenceConfig().set_name("items"))
        self.marker_description = RegExpPersistence(RegExpConfig().set_name("marker_description").set_match("->"))
        self.description = RegExpPersistence(RegExpConfig().set_name("description").set_match(r"[^$]+").set_separator("-- "))

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
        (color_name, after_color_name) = self.color_name.parse_ctx_string(ctx, after_emails)
        after_marker_items = self.marker_items.consume_marker(ctx, after_color_name)
        (items_strlist, after_items) = self.items.parse_ctx_list(ctx, after_marker_items)
        items = [self.item.parse(ctx, item) for item in items_strlist]
        after_marker_description = self.marker_description.consume_marker(ctx, after_items)
        (description, _) = self.description.parse_ctx_string(ctx, after_marker_description)
        spareRow = SpareRow()
        spareRow.set_id(id)
        spareRow.set_v_int_as_str(v_int)
        spareRow.set_url(url)
        spareRow.set_tags(tags)
        spareRow.set_emails(emails)
        spareRow.set_color_name_as_str(color_name)
        spareRow.set_items(items)
        spareRow.set_description(description)
        return spareRow

class SpareSectionParser(LineParser):
    def __init__(self):
        self.marker_section = RegExpPersistence(RegExpConfig().set_name("marker_section_row").set_match("section"))
        self.section_type= EnumPersistence(EnumConfig().set_name("section_type").set_values(["alpha", "beta",]))

    def parse(self, ctx: ParsingContext, chunk: str)->SpareSection:
        after_marker = self.marker_section.consume_marker(ctx, chunk)
        (section_type, _) = self.section_type.parse_ctx_string(ctx, after_marker)
        spareSection = SpareSection()
        spareSection.set_section_type_as_str(section_type)
        return spareSection

class SpareDocSectionAlpha:
    def __init__(self):
        self.header = SpareSection()
        self.rows: List[SpareRow] = []

    def set_header(self, header: SpareSection):
        self.header = header
        return self

    def add_row(self, row: SpareRow):
        self.rows.append(row)
        return self

    def to_nmo_string_list(self)->List[str]:
       return [self.header.to_nmo_string()] + [ row.to_nmo_string() for row in self.rows]
    
    def to_string(self):
        return "\n".join(self.to_nmo_string_list())

    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
            return self.to_string() == str(other)

class SpareDocSectionBeta:
    def __init__(self):
        self.header1 = SpareSection()
        self.rows = []

    def set_header1(self, header: SpareSection):
        self.header1 = header
        return self

    def add_row(self, row: SpareRow):
        self.rows.append(row)
        return self

    def to_nmo_string_list(self)->List[str]:
       return [self.header1.to_nmo_string()] + [ row.to_nmo_string() for row in self.rows]

    def to_string(self):
        return "\n".join(self.to_nmo_string_list())

    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
            return self.to_string() == str(other)

class SpareDoc:
    def __init__(self):
        self.separator = "--------"
        self.section_alpha = SpareDocSectionAlpha()
        self.section_beta = SpareDocSectionBeta()

    def to_nmo_string_list(self)->List[str]:
       return self.section_alpha.to_nmo_string_list()+[self.separator]+self.section_beta.to_nmo_string_list()
    
    def to_nmo_string(self)->str:
        return "\n".join(self.to_nmo_string_list())

    def __str__(self):
        return self.to_nmo_string()
    
    def __repr__(self):
        return self.to_nmo_string()

    def __eq__(self, other):
            return self.to_nmo_string() == other.to_nmo_string()


class SpareParser:
    def __init__(self):
        self.separator = "--------"
        self.comment_prefix = "#"
        self.init_row_detector()
        self.init_script_parser()

    def init_row_detector(self):
        row_detector = RowDetector()
        row_detector.add_option(RowDetectorOption().set_name("section_alpha").set_separator(" ").set_prefixes(["section", "alpha"]))
        row_detector.add_option(RowDetectorOption().set_name("section_beta").set_separator(" ").set_prefixes(["section", "beta"]))
        row_detector.add_option(RowDetectorOption().set_name("row").set_separator(" ").set_prefixes(["row"]))
        self.row_detector = row_detector

    def init_script_parser(self):
        script_parser = ScriptParser()
        script_parser.add_line_parser_cfg(LineParserConfig().set_scope("section_alpha").set_name("section_alpha").set_single().set_parser(SpareSectionParser()))
        script_parser.add_line_parser_cfg(LineParserConfig().set_scope("section_beta").set_name("section_beta").set_single().set_parser(SpareSectionParser()))
        script_parser.add_line_parser_cfg(LineParserConfig().set_scope("_").set_name("row").set_multiple().set_parser(SpareRowParser()))
        self.script_parser = script_parser

    def parse(self, refctx: ParsingContext, content: str)->SpareDoc:
        spareDoc = SpareDoc()
        lines = content.splitlines()
        scope = "?"
        for idx, linecr in enumerate(lines):
            line = linecr.strip()
            ctx = ParsingContext().set_id(refctx.id).set_line_number(idx)
            if len(line) == 0:
                continue
            if line.startswith(self.comment_prefix):
                continue
            if line.startswith(self.separator):
                scope = "?"
                continue
            name = self.row_detector.match(line)
            if name is None:
                raise PersistenceParserError(ctx, name, line) 
            line_parser_cfg = self.script_parser.line_parser_configs[name]
            typedobj = line_parser_cfg.parser.parse(ctx,line)
            if not (line_parser_cfg.scope == "_" ):
                scope = line_parser_cfg.scope
            if len(scope) <=1:
                raise PersistenceParserError(ctx, name, line)
            if scope == 'section_alpha':
                if name == 'section_alpha':
                    spareDoc.section_alpha.header1 = typedobj
                elif name == 'row':
                    spareDoc.section_alpha.rows.append(typedobj)
            elif scope == 'section_beta':
                if name == 'section_beta':
                    spareDoc.section_beta.header1 = typedobj
                elif name == 'row':
                    spareDoc.section_beta.rows.append(typedobj)
            else:
                raise PersistenceParserError(ctx, name, line)
        return spareDoc
    