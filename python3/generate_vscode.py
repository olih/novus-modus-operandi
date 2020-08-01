from ast import parse, dump, ImportFrom, FunctionDef
import astor
from astor.tree_walk import TreeWalk
# https://github.com/berkerpeksag/astor

def load_tree():
    return astor.parse_file('python3/spare_vscode.py')

def to_string(tree):
    return astor.to_source(tree)

codetree = load_tree()


def generate_simple_field(newname: str):
    for body in codetree.body:
        if isinstance(body, FunctionDef) is True:
            if (body.name == "simple_field"):
                body.name = newname
                return to_string(body)


print(generate_simple_field("alpha"))