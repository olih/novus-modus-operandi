from ast import parse, dump, ImportFrom, FunctionDef, ClassDef, Assign
import astor
from astor.tree_walk import TreeWalk
from copy import deepcopy
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

def find_class(classname: str):
    for body in codetree.body:
        if isinstance(body, ClassDef) is True:
            if (body.name == classname):
                return body
    return None

def find_assigns(node):
    return [n for n in node if isinstance(n, Assign) is True]

def print_types(something):
    for part in something.body:
        print(type(part))


#SpareFormatter
def generate_formatter(newname: str)->str:
    for body in codetree.body:
        if isinstance(body, ClassDef) is True:
            if (body.name == "SpareFormatter"):
                body.name = newname
                return to_string(body)

def alter_name_assigmnent( assignment: Assign, newname: str):
    newassign = deepcopy(assignment)
    newassign.targets[0].id = newname
    return newassign

def generate_enum(config: GenEnumConfig)->str:
    newclass = find_class("ColorName")
    newclass.name = config.name
    assigments = find_assigns(newclass.body)
    new_assignments = [ alter_name_assigmnent(assigments[0], name) for name in config.get_values_as_const()]
    del(newclass.body[1])
    del(newclass.body[0])
    for new_assignment in new_assignments:
        newclass.body.insert(0, new_assignment)
    return to_string(newclass) 

save_code_file("python3/generated.py",
    [   generate_imports(),
        generate_formatter("MyFormatter"),
        generate_enum(GenEnumConfig().set_name("MyEnum").set_values(["randint", "randfraction"]))
    ]
)