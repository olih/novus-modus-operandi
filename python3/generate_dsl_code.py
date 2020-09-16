from ast import parse, dump, ImportFrom, FunctionDef, ClassDef
import astor
from astor.tree_walk import TreeWalk
from typing import List, Tuple, Dict, Set
from dsl_gen_helper import GenEnumConfig

# https://github.com/berkerpeksag/astor

def load_tree():
    return astor.parse_file('python3/spare_dsl.py')

def to_string(tree):
    return astor.to_source(tree)

codetree = load_tree()

def save_code_file(filename, blocks: List[str]):
    with open(filename, 'w') as codefile:
        content = "\n\n".join(blocks)
        codefile.write(content)

#SpareFormatter
def generate_imports()->str:
    results = [to_string(body) for body in codetree.body if isinstance(body, ImportFrom) is True]
    return "".join(results)        

#SpareFormatter
def generate_formatter(newname: str)->str:
    for body in codetree.body:
        if isinstance(body, ClassDef) is True:
            if (body.name == "SpareFormatter"):
                body.name = newname
                return to_string(body)


def generate_enum(config: GenEnumConfig)->str:
    for body in codetree.body:
        if isinstance(body, ClassDef) is True:
            if (body.name == "ColorName"):
                body.name = config.name
                return to_string(body)


save_code_file("python3/generated.py",
    [   generate_imports(),
        generate_formatter("MyFormatter"),
        generate_enum(GenEnumConfig().set_name("MyEnum").set_values(["randint", "randfraction"]))
    ]
)