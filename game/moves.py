from forseti.move import Move
from dataclasses import dataclass
from enum import Enum

class MovementDirections(Enum):
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4

@dataclass
class PlayerMovement(Move):

    direction: MovementDirections
    distance: int
