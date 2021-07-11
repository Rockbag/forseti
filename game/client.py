from forseti.engine import CheatEngine, CheatEngineConfig
from forseti.vote import Vote
from game.players import Player, Cheater

from game.rules import MovementRule
from game.moves import PlayerMovement
from typing import Set

from game.moves import MovementDirections
from game.game_state import game_state


class GameClient:
    """
    This class just represents a virtual game client. This is needed here to demonstrate how the engine works.
    """
    
    def __init__(self, player_ids: Set[int], current_player: Player):
        self.player = current_player
        self.cheat_engine = CheatEngine(
            CheatEngineConfig(
                rules={ PlayerMovement.hash(): MovementRule()},
                player_ids = player_ids,
                current_player_id=current_player.id,
                move_processing_time_in_seconds=0.1,
                consensus_percentage=51,
                cheating_tolerance=1,
                player_registration_timeout=10
                )
        )
        self.cheat_engine.events.on_player_cheated += self.player_cheated


    def move_player(self, distance: int):
        """
        Moves the player with the distance provided.
        """
        self.player.move(MovementDirections.FORWARD)


    def join_players(self, players: Set[Player]):
        """
        Registers that a player has joined the game.
        When the player joins, we subscribe to their events. Networking libraries will usually expose a callback like "OnPlayerConnected" for this.
        """
        for player in players:
            self.cheat_engine.register_player(player.id)
            game_state.add_player(player)
            player.events.on_player_moved += self.player_moved   
            player.events.on_player_voted += self.player_voted     

    def player_cheated(self, cheater_id: int):
        """
        Once a player is deemed to be cheating, we no longer care about their inputs. It's as if they didn't event exist.
        """
        print(f"Player {self.player.id} is unsubbing from Player {cheater_id}'s events")
        game_state.get_player(cheater_id).events.on_player_moved -= self.player_moved

    def player_moved(self, movement: PlayerMovement):
        """
        Once a player moves, we push their movement through the cheat engine running on our client. This is true for every game client (that is not hacked)
        """
        self.cheat_engine.register_move(movement)

    def player_voted(self, vote: Vote):
        self.cheat_engine.register_vote(vote)
