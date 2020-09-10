from ast import parse, dump, ImportFrom, FunctionDef, ClassDef
import astor
from astor.tree_walk import TreeWalk
from typing import List, Tuple, Dict, Set

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
def generate_formatter(newname: str):
    for body in codetree.body:
        if isinstance(body, ClassDef) is True:
            if (body.name == "SpareFormatter"):
                body.name = newname
                return to_string(body)



save_code_file("python3/generated.py",
    [ generate_formatter("MyFormatter")
    ]
)