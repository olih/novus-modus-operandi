from ast import parse, dump, ImportFrom, FunctionDef, ClassDef, Assign, If, Compare, Name, Attribute, Return, Str, Module, Eq
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

def find_method(classDef: ClassDef, methodname: str):
    for body in classDef.body:
        if isinstance(body, FunctionDef) is True:
            if (body.name == methodname):
                return body
    return None

def find_assigns(node):
    return [n for n in node if isinstance(n, Assign) is True]

def print_types(something):
    if "body" in something:
        for part in something.body:
            print(type(part))
    else:
        print(something)


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

def change_name(name: Name, newname: str):
    brandnewname = deepcopy(name)
    brandnewname.id = newname
    return brandnewname

def change_enum(attr: Attribute, classname: str, enumvalue: str):
    newattr = deepcopy(attr)
    newattr.value.id = classname
    newattr.attr = enumvalue
    return change_enum

def new_attribute(classname: str, enumvalue: str)->Attribute:
    return Attribute(Name(classname), enumvalue)

def new_compare_value_equal(attr: Attribute)->Compare:
    return Compare(Name("value"),[Eq()], [attr])

def new_str(value: str):
    return Str(value)

def new_return_str(value: str):
    return Return(new_str(value))

def gen_if_enum(classname: str, enumvalue: str, str_return: str, otherwise):
    test = new_compare_value_equal(new_attribute(classname, enumvalue))
    body = [new_return_str(str_return)]
    orelse = [otherwise]
    newif = If(test, body, orelse)
    return newif

def gen_ifs_enum(classname: str, enum_and_value_list: List[Tuple[str]], otherwise: str):
    elsewise = new_return_str(otherwise)
    result = elsewise
    for ev in sorted(enum_and_value_list):
        result = gen_if_enum(classname, ev[0], ev[1], result)
    return result

def generate_enum(config: GenEnumConfig)->str:
    newclass = find_class("ColorName")
    newclass.name = config.name
    from_nmo_string = find_method(newclass, "from_nmo_string")
    to_nmo_string = find_method(newclass, "to_nmo_string")
    body_to_nmo_string = gen_ifs_enum(config.name, config.get_values_as_const_and_val(), "E")
    print(to_string(body_to_nmo_string))
    to_nmo_string.body[0] = body_to_nmo_string
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
        generate_enum(GenEnumConfig().set_name("MyEnum").set_values(["randint", "randfraction", "randfloat"]))
    ]
)