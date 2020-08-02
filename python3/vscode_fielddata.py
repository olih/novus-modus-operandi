from typing import List, Tuple, Dict, Set
import json

class TmFieldKindData:
    def __init__(self, content):
        self.name: str = content["name"]
        self.spare_function: str = content["spare-function"]
        self.description: str = content["description"]
        self.scope: str = content["scope"]
        self.match: str = content["match"]
        self.keywords: List[str] = content["keywords"]
        self.start: str = content["start"]
        self.finish: str = content["finish"]
        self.examples: List[str] = content["examples"]
        self.counter_examples: List[str] = content["counter-examples"]


class TmFieldKindDataList:
    def __init__(self):
        self.fields: TmFieldKindData  = []

    def load(self, filename):
        with open(filename, 'r') as jsonfile:
            content = json.load(jsonfile)
            self.fields = [TmFieldKindData(item) for item in content]

    def __str__(self):
        return "Lentgh: {}".format(len(self.fields))

data_list = TmFieldKindDataList()
data_list.load("python3/nmo_fielddata.json")

print(data_list)