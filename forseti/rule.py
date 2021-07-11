
from dataclasses import dataclass
from forseti.move import Move

@dataclass
class Rule:
    """
    Defines a rule to be matched against.
    """
    
    def evaluate(self, move: Move):
        return True, ''

    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, o):
        return self == o
