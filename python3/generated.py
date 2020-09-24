from typing import List, Tuple, Dict, Set, Optional
from fractions import Fraction
from enum import Enum, auto
from dsl_text import SequenceConfig, SequencePersistence, RegExpConfig, RegExpPersistence, IntegerConfig, IntegerPersistence, BriefAnswer
from dsl_text import FloatConfig, FloatPersistence, FractionConfig, FractionPersistence, EnumConfig, EnumPersistence
from dsl_text import PersistenceSequence, PersistenceParserError, ParsingContext, BasePersistence
from dsl_text import RowDetectorOption, RowDetector, LineParser, LineParserConfig, ScriptParser


class MyFormatter:

    def __init__(self):
        self.tags = SequencePersistence(SequenceConfig().set_name('tags').
            set_start('[').set_finish(']').set_separator(' '))
        self.emails = SequencePersistence(SequenceConfig().set_name(
            'emails').set_start('[').set_finish(']').set_separator(' '))
        self.items = SequencePersistence(SequenceConfig().set_name('items')
            .set_start('[').set_finish(']').set_separator(','))

    def from_int(self, value: int) ->str:
        return str(value)

    def from_float(self, value: float) ->str:
        return str(value)

    def from_url(self, value: str) ->str:
        return value.strip()

    def from_id(self, value: str) ->str:
        return value.strip()

    def from_tag(self, value: str) ->str:
        return value.strip()

    def from_email(self, value: str) ->str:
        return value.strip()

    def from_fraction(self, value: Fraction) ->str:
        return str(value)

    def from_tags(self, values: List[str]) ->str:
        return self.tags.to_csv_string([self.from_tag(value) for value in
            values])

    def from_emails(self, values: List[str]) ->str:
        return self.emails.to_csv_string([self.from_email(value) for value in
            values])

    def from_items(self, values: List[str]) ->str:
        return self.items.to_csv_string(values)


class MyEnum(Enum):
    RANDFLOAT = auto()
    RANDFRACTION = auto()
    RANDINT = auto()
    NOT_SUPPORTED = auto()

    @classmethod
    def from_nmo_string(cls, value: str):
        if value == 'red':
            return ColorName.RED
        elif value == 'green':
            return ColorName.GREEN
        else:
            return ColorName.NOT_SUPPORTED

    @classmethod
    def to_nmo_string(cls, value):
        if value == ColorName.RED:
            return 'red'
        elif value == ColorName.GREEN:
            return 'green'
        else:
            return 'E'
