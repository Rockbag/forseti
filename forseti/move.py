from dataclasses import dataclass

@dataclass(order=True)
class Move:
    """
    High-level class that represent a move. Inherit from this to create specific moves that need to be checked against.

      Parameters:
        player_id: the id of the player making the move
    """
    
    priority: int
    player_id: int

    @classmethod
    def hash(cls):
      return hash(cls.__name__)

    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, o):
        return self == o
