from forseti.engine import CheatEngine, CheatEngineConfig
from game.players import Player, Cheater

from game.rules import MovementRule
from game.moves import PlayerMovement
from game.client import GameClient

player_1 = Player(1)
player_2 = Player(2)
player_3 = Player(3)
player_4 = Player(4)
cheater = Cheater(5)

player_ids = {player_1.id, player_2.id, player_3.id, player_4.id, cheater.id}

# Virtual game clients. Needed only for demonstration. Generally your game client is your game code basically.
# Since this demo is attempting to simulate multiple players connecting to each other, we need to specify multiple clients.
game_client_1 = GameClient(player_ids, player_1)
game_client_2 = GameClient(player_ids, player_2)
game_client_3 = GameClient(player_ids, player_3)
game_client_4 = GameClient(player_ids, player_4)
game_client_5 = GameClient(player_ids, cheater)

game_client_1.join_players({player_2, player_3, player_4, cheater})
game_client_2.join_players({player_1, player_3, player_4, cheater})
game_client_3.join_players({player_1, player_2, player_4, cheater})
game_client_4.join_players({player_1, player_2, player_3, cheater})
game_client_5.join_players({player_1, player_2, player_3, player_4})

# Let's move all the players by one (their max speed).
game_client_1.move_player(1)
game_client_2.move_player(1)
game_client_3.move_player(1)
game_client_4.move_player(1)

# Now the cheater tries to move 5, which is well above their max speed.
game_client_5.move_player(5)
quit()