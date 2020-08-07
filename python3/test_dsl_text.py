import unittest
from random import randint, choice
from typing import List, Tuple, Dict, Set, Optional
from dsl_text import SequenceConfig, SequencePersistence, RegExpConfig, RegExpPersistence, IntegerConfig, IntegerPersistence, FloatConfig, FloatPersistence, FractionConfig, FractionPersistence, BriefAnswer

squareSequenceCfg = SequenceConfig().set_start(
    "[").set_finish("]").set_separator(",")
parenthesisSequenceCfg = SequenceConfig().set_start(
    "(").set_finish(")").set_separator("||")
curlySequenceCfg = SequenceConfig().set_start(
    "{").set_finish("}").set_separator(";")
cfgs = [squareSequenceCfg, parenthesisSequenceCfg, curlySequenceCfg]

def str_random_padding(value: str)->str:
    which = randint(1, 12)
    if which <= 3:
        return value
    elif which <= 6:
        return " {}".format(value)
    elif which <= 9:
        return "{} ".format(value)
    else:
        return " {} ".format(value)

def add_in_middle(value: str, corruption: str)->str:
    middle = len(value) // 2
    return value[:middle]+corruption+value[middle+1:]

def str_random_corrupt_by_removal(value: str, to_remove: List[str])->str:
    corruption = choice(to_remove)
    return value.replace(corruption, "", 1)

def str_random_corrupt_by_addition(value: str, to_add: List[str])->str:
    corruption = choice(to_add)
    return add_in_middle(value, corruption)

def list_random_padding(values: List[str])->List[str]:
    return [str_random_padding(value) for value in values]


class TestSequencePersistence(unittest.TestCase):

    def test_satisfy_should_succeed(self):
        examples = [
            ["one-value"],
            ["one", "two", "three"]
            ]
        for cfg in cfgs:
            seqPersist = SequencePersistence(cfg)
            for ex in examples:
                    and_more = " and more"
                    chunkstr = seqPersist.to_csv_string(list_random_padding(ex)) + and_more
                    with self.subTest(cfg=cfg, ex=ex):
                        self.assertTrue(seqPersist.satisfy(chunkstr))
                        self.assertSequenceEqual(seqPersist.parse_as_list(chunkstr), (ex, and_more))
    
    def test_satisfy_should_fail(self):
        counter_examples = [
            ["one-value"],
            ["one", "two", "three"]
            ]
        for cfg in cfgs:
            seqPersist = SequencePersistence(cfg)
            for ex in counter_examples:
                    and_more = " and more"
                    chunkstr = seqPersist.to_csv_string(list_random_padding(ex)) + and_more
                    corrupted = str_random_corrupt_by_removal(chunkstr, to_remove = [seqPersist.cfg.start, seqPersist.cfg.finish])
                    with self.subTest(cfg=cfg, ex=ex):
                        self.assertFalse(seqPersist.satisfy(corrupted))

class TestRegExpPersistence(unittest.TestCase):

    def test_satisfy_should_succeed(self):
        use_cases = [
            { "cfg": RegExpConfig().set_separator(" ").set_match(r"^([a-z]+)(\s+|$)"),
              "examples": ["abc", "a"*10]
            }
            ]
        for use_case in use_cases:
            cfg = use_case["cfg"]
            rePersist = RegExpPersistence(cfg)
            for ex in use_case["examples"]:
                and_more = "and more"
                chunkstr = ex + " " + and_more
                with self.subTest(cfg=cfg, ex=ex):
                    self.assertTrue(rePersist.satisfy(chunkstr))
                    self.assertSequenceEqual(rePersist.parse_as_string(chunkstr), (ex, and_more))

    def test_satisfy_should_fail(self):
        use_cases = [
            { "cfg": RegExpConfig().set_separator(" ").set_match(r"^([a-z]+)(\s+|$)"),
              "examples": ["123", "abcDEF"]
            }
            ]
        for use_case in use_cases:
            cfg = use_case["cfg"]
            rePersist = RegExpPersistence(cfg)
            for ex in use_case["examples"]:
                and_more = " and more"
                chunkstr = ex + and_more
                with self.subTest(cfg=cfg, ex=ex):
                    self.assertFalse(rePersist.satisfy(chunkstr))

class TestIntegerPersistence(unittest.TestCase):

    def test_satisfy_should_succeed(self):
        use_cases = [
            { "cfg": IntegerConfig().set_separator(" ").set_has_sign(BriefAnswer.Yes),
              "examples": ["+1", "+123", "0", "-1234"]
            },
            { "cfg": IntegerConfig().set_separator(" ").set_has_sign(BriefAnswer.No),
              "examples": ["1", "123", "0"]
            },
            { "cfg": IntegerConfig().set_separator(" ").set_has_sign(BriefAnswer.Maybe),
              "examples": ["+1", "+123", "0", "-1234", "3"]
            },
            { "cfg": IntegerConfig().set_separator(";").set_has_sign(BriefAnswer.Yes),
              "examples": ["+1", "+123", "0", "-1234"]
            },
            { "cfg": IntegerConfig().set_separator(",").set_has_sign(BriefAnswer.No),
              "examples": ["1", "123", "0"]
            },
             ]
        for use_case in use_cases:
            cfg = use_case["cfg"]
            rePersist = IntegerPersistence(cfg)
            for ex in use_case["examples"]:
                and_more = "and more"
                sep = cfg.separator
                chunkstr = ex + sep + and_more
                with self.subTest(cfg=cfg, ex=ex):
                    self.assertTrue(rePersist.satisfy(chunkstr))
                    self.assertSequenceEqual(rePersist.parse_as_string(chunkstr), (ex, and_more))
                    self.assertSequenceEqual(rePersist.parse_as_string(ex), (ex, ""))

    def test_satisfy_should_fail(self):
        use_cases = [
            { "cfg": IntegerConfig().set_separator(" ").set_has_sign(BriefAnswer.Yes),
              "examples": ["+a", "+", "", "3.14"]
            },
            { "cfg": IntegerConfig().set_separator(" ").set_has_sign(BriefAnswer.No),
              "examples": ["+a", "+", "",  "3.14"]
            },
            { "cfg": IntegerConfig().set_separator(" ").set_has_sign(BriefAnswer.Maybe),
              "examples": ["+a", "+", "", "3.14"]
            },
            { "cfg": IntegerConfig().set_separator(";").set_has_sign(BriefAnswer.Yes),
              "examples": ["+a", "+", "", "3.14"]
            },
            { "cfg": IntegerConfig().set_separator(",").set_has_sign(BriefAnswer.No),
              "examples": ["+a", "+", ""]
            },
             ]
        for use_case in use_cases:
            cfg = use_case["cfg"]
            rePersist = IntegerPersistence(cfg)
            for ex in use_case["examples"]:
                and_more = "and more"
                sep = cfg.separator
                chunkstr = ex + sep + and_more
                with self.subTest(cfg=cfg, ex=ex):
                    self.assertFalse(rePersist.satisfy(chunkstr))

class TestFloatPersistence(unittest.TestCase):

    def test_satisfy_should_succeed(self):
        use_cases = [
            { "cfg": FloatConfig().set_separator(" ").set_has_sign(BriefAnswer.Yes),
              "examples": ["+1", "+123", "0", "-1234", "+0.19", "-3.14"]
            },
            { "cfg": FloatConfig().set_separator(" ").set_has_sign(BriefAnswer.No),
              "examples": ["1", "123", "0", "2.13"]
            },
            { "cfg": FloatConfig().set_separator(" ").set_has_sign(BriefAnswer.Maybe),
              "examples": ["+1", "+123", "0", "-1234", "3", "4.12"]
            },
            { "cfg": FloatConfig().set_separator(";").set_has_sign(BriefAnswer.Yes),
              "examples": ["+1", "+123", "0", "-1234", "+2.15"]
            },
            { "cfg": FloatConfig().set_separator(",").set_has_sign(BriefAnswer.No),
              "examples": ["1", "123", "0"]
            },
             ]
        for use_case in use_cases:
            cfg = use_case["cfg"]
            rePersist = FloatPersistence(cfg)
            for ex in use_case["examples"]:
                and_more = "and more"
                sep = cfg.separator
                chunkstr = ex + sep + and_more
                with self.subTest(cfg=cfg, ex=ex):
                    self.assertTrue(rePersist.satisfy(chunkstr))
                    self.assertSequenceEqual(rePersist.parse_as_string(chunkstr), (ex, and_more))
                    self.assertSequenceEqual(rePersist.parse_as_string(ex), (ex, ""))

    def test_satisfy_should_fail(self):
        use_cases = [
            { "cfg": FloatConfig().set_separator(" ").set_has_sign(BriefAnswer.Yes),
              "examples": ["+a", "+", ""]
            },
            { "cfg": FloatConfig().set_separator(" ").set_has_sign(BriefAnswer.No),
              "examples": ["+a", "+", ""]
            },
            { "cfg": FloatConfig().set_separator(" ").set_has_sign(BriefAnswer.Maybe),
              "examples": ["+a", "+", ""]
            },
            { "cfg": FloatConfig().set_separator(";").set_has_sign(BriefAnswer.Yes),
              "examples": ["+a", "+", ""]
            },
            { "cfg": FloatConfig().set_separator(",").set_has_sign(BriefAnswer.No),
              "examples": ["+a", "+", ""]
            },
             ]
        for use_case in use_cases:
            cfg = use_case["cfg"]
            rePersist = FloatPersistence(cfg)
            for ex in use_case["examples"]:
                and_more = "and more"
                sep = cfg.separator
                chunkstr = ex + sep + and_more
                with self.subTest(cfg=cfg, ex=ex):
                    self.assertFalse(rePersist.satisfy(chunkstr))

class TestFractionPersistence(unittest.TestCase):

    def test_satisfy_should_succeed(self):
        use_cases = [
            { "cfg": FractionConfig().set_separator(" ").set_has_sign(BriefAnswer.Yes),
              "examples": ["+1", "+123", "0", "-1234", "+0.19", "-3.14"]
            },
            { "cfg": FractionConfig().set_separator(" ").set_has_sign(BriefAnswer.No),
              "examples": ["1", "123", "0", "2.13"]
            },
            { "cfg": FractionConfig().set_separator(" ").set_has_sign(BriefAnswer.Maybe),
              "examples": ["+1", "+123", "0", "-1234", "3", "4.12"]
            },
            { "cfg": FractionConfig().set_separator(";").set_has_sign(BriefAnswer.Yes),
              "examples": ["+1", "+123", "0", "-1234", "+2.15"]
            },
            { "cfg": FractionConfig().set_separator(",").set_has_sign(BriefAnswer.No),
              "examples": ["1", "123", "0"]
            },
             ]
        for use_case in use_cases:
            cfg = use_case["cfg"]
            rePersist = FractionPersistence(cfg)
            for ex in use_case["examples"]:
                and_more = "and more"
                sep = cfg.separator
                chunkstr = ex + sep + and_more
                with self.subTest(cfg=cfg, ex=ex):
                    self.assertTrue(rePersist.satisfy(chunkstr))
                    self.assertSequenceEqual(rePersist.parse_as_string(chunkstr), (ex, and_more))
                    self.assertSequenceEqual(rePersist.parse_as_string(ex), (ex, ""))

    def test_satisfy_should_fail(self):
        use_cases = [
            { "cfg": FractionConfig().set_separator(" ").set_has_sign(BriefAnswer.Yes),
              "examples": ["+a", "+", ""]
            },
            { "cfg": FractionConfig().set_separator(" ").set_has_sign(BriefAnswer.No),
              "examples": ["+a", "+", ""]
            },
            { "cfg": FractionConfig().set_separator(" ").set_has_sign(BriefAnswer.Maybe),
              "examples": ["+a", "+", ""]
            },
            { "cfg": FractionConfig().set_separator(";").set_has_sign(BriefAnswer.Yes),
              "examples": ["+a", "+", ""]
            },
            { "cfg": FractionConfig().set_separator(",").set_has_sign(BriefAnswer.No),
              "examples": ["+a", "+", ""]
            },
             ]
        for use_case in use_cases:
            cfg = use_case["cfg"]
            rePersist = FractionPersistence(cfg)
            for ex in use_case["examples"]:
                and_more = "and more"
                sep = cfg.separator
                chunkstr = ex + sep + and_more
                with self.subTest(cfg=cfg, ex=ex):
                    self.assertFalse(rePersist.satisfy(chunkstr))
