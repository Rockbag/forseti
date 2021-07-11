from abc import ABC
from game.moves import MovementDirections
from dataclasses import dataclass
from events import Events
from game.rules import MovementRule
from game.moves import PlayerMovement
from forseti.engine import CheatEngine, CheatEngineConfig
from forseti.vote import Vote

class Player(ABC):

    def __init__(self, id: int):
        self.id = id
        self.max_speed = 1
        self.events = Events(('on_player_moved', 'on_player_voted'))


    def move(self, move_direction: MovementDirections):
        movement = PlayerMovement(player_id=self.id, priority=0, direction=MovementDirections.FORWARD, distance=self.max_speed)

        # This is the client-side validation of the movement. A cracked client can override this and get rid of the check if they wanted to, but our good player runs with it as they should.
        valid, msg = MovementRule().evaluate(movement)
        if not valid:
            print(f"Wrong move - {msg}")
            return

        # Note that this just propagates the event in-memory since this example does not use networking.
        # However, in a multiplayer game this is where you'd broadcast the movement.
        self.events.on_player_moved(movement)

    def vote(self, vote: Vote):
        self.events.on_player_voted(vote)


class Cheater(Player):
    """
    A player who likes to cheat.
    """
    
    def move(self, move_direction: MovementDirections):
        movement = PlayerMovement(player_id= self.id, priority=0, direction=MovementDirections.FORWARD, distance=5)

        # Notice how this cheater player does not validate the movement on their side, so the event gets broadcasted to the network
        # regardless if it's valid or not.

        self.events.on_player_moved(movement)