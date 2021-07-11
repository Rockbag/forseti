from dataclasses import dataclass
from typing import Dict
from game.players import Player


class GameState:

    def __init__(self):
        self.players = dict()

    def add_player(self, player: Player):
        self.players[player.id] = player

    def get_player(self, player_id):
        return self.players.get(player_id)

    def remove_player(self, player_id):
        del self.players[player_id]


game_state = GameState()
