from forseti.rule import Rule
from forseti.move import Move
from game.moves import PlayerMovement
from typing import cast

class MovementRule(Rule):
    """
    A simple rule that makes sure a player cannot move more than their max_speed.
    """

    def evalute(self, move: Move):
        move: PlayerMovement = cast(PlayerMovement, move)

        from game.game_state import game_state
        player = game_state.get_player(move.player_id)
        msg = f"Player {player.id} is attempting to move distance {move.distance} with max speed of {player.max_speed}"
        return move.distance <= player.max_speed, msg
