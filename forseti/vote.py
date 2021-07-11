from dataclasses import dataclass
from forseti.move import Move

@dataclass
class Vote:
    """
    A vote cast by a connected client about a specific move that happened in the game.
    
      Parameters:
        move: a move to vote on made by another player.
        player_id: the id of the player casting the vote.
        value: wether the move was accepted or not.
    """
    move: Move
    accuser_id: int
    suspect_id: int
    value: bool


    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, o):
        return self == o
