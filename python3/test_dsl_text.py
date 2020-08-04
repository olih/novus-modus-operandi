import unittest
from random import randint
from typing import List, Tuple, Dict, Set, Optional
from dsl_text import SequenceConfig, SequencePersistence

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

def list_random_padding(values: List[str])->List[str]:
    return [str_random_padding(value) for value in values]

class TestSequencePersistence(unittest.TestCase):

    def test_satisfy(self):
        # should match
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


        # should not match
