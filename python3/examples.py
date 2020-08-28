from typing import List, Tuple, Dict, Set, Optional, Union
import json
from random import choice, sample


class Examples:
    def __init__(self):
        self.valid = []
        self.invalid = []

    def pick_valid(self):
        return choice(self.valid)

    def pick_invalid(self):
        return choice(self.valid)

    def sample_valid(self, k: int):
        return sample(self.valid, k)
    
    def sample_invalid(self, k: int):
        return sample(self.invalid, k)
    
    def load(self, filename: str):
        with open(filename, 'r') as jsonfile:
            examples = json.load(jsonfile)
            self.valid = examples["valid"]
            self.invalid = examples["invalid"]
            return self

