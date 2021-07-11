
from dataclasses import dataclass
from forseti.vote import Vote
from forseti.move import Move
from forseti.rule import Rule
from typing import List, Optional, Dict, Set, Type
from events import Events
from threading import Thread
from queue import PriorityQueue
import time

class InvalidMoveConfiguration(Exception):
    
    def __init__(self, move_type: Type[Move], msg: str):
        self.move_type = move_type
        self.msg = msg

@dataclass
class CheatEngineConfig:
    """
    Configuration for the cheat engine.

      Parameters:
        rules: A dictionary mapping moves to rules. A move will be evaluated against a Rule it's matched with. Use an integer as a move id.
        player_ids: The id of each player in the game. Here we assume that by the time the game launches, players already know who they are facing against. I.e. there's a pregame lobby.
        consensus_percentage: The percentage of votes at which the engine should declare someone a cheater. Default is 51, so majority.
        cheating_tolerance: How many times can a player be considered to issue a cheating move before being booted. Defaults to 1.
        current_player_id: The id of the player running this client.
        move_processing_time_in_seconds: Defines, in seconds, how long the background thread should wait between processing moves. Default is 0.1s
        player_registration_timeout: Defines, in seconds, how much time a player client has to register into the cheat detection system. If the timeout passes and the client failed to register, the client automatically deemed as a cheater.
    """

    rules: Dict[int, Rule]
    player_ids: Set[int]
    current_player_id: int
    move_processing_time_in_seconds: int = 0.1
    consensus_percentage: Optional[int] = 51
    cheating_tolerance: int = 1
    player_registration_timeout: int = 10


class CheatEngine:
    """
    Parameters:
      _votes: A dictionary keeping track of people who were accused and by whom they were accused. This is used reach a consensus on who's a cheater.
    """

    events: Events
    _player_ids: Set[int]
    _moves_queue: PriorityQueue
    _rules: Dict[int, Rule]
    _votes = Dict[int, List[int]]
    _cheaters = List[int]

    _move_processor: Thread
    _move_processor_sleep_interval: int
    _current_player_id: int

    _registered_player_ids: Set[int]
    _player_registration_timeout: int

    def __init__(self, cheat_engine_config: CheatEngineConfig):
        self.events = Events(('on_player_cheated', 'on_player_registered'))
        self._player_ids = cheat_engine_config.player_ids - {cheat_engine_config.current_player_id}
        self._consensus_percentage = cheat_engine_config.consensus_percentage
        self._moves_queue = PriorityQueue()
        self._rules = cheat_engine_config.rules
        self._votes = dict()
        self._cheaters = []
        self._current_player_id = cheat_engine_config.current_player_id
        self._player_registration_timeout = cheat_engine_config.player_registration_timeout
        Thread(target=self._check_player_registrations, daemon=False).start()
        self._move_processor_sleep_interval = cheat_engine_config.move_processing_time_in_seconds
        self._move_processor = Thread(target=self._process_moves, daemon=False)
        
        self._move_processor.start()
        self.events.on_player_registered(cheat_engine_config.current_player_id)
        self._registered_player_ids = set()

    def register_player(self, player_id: int):
        self._registered_player_ids.add(player_id)

    def register_move(self, move: Move):
        self._moves_queue.put(move)

    def register_vote(self, vote: Vote):
        if vote.suspect_id not in self._votes:
            self._votes[vote.suspect_id] = [vote.accuser_id]
        else:
            self._votes[vote.suspect_id].append(vote.accuser_id)
        self.check_consensus(vote)
            
    def _check_player_registrations(self):
        """
        Threaded function that checks if players have registered within the configured timeout period.
        Any player who failed to register is considered a cheater on this client.
        """
        time.sleep(self._player_registration_timeout)
        for player_id in self._player_ids - self._registered_player_ids:
            self.events.on_player_cheated(player_id)
            self._cheaters.append(player_id)


    def _process_moves(self):
        """
        Threaded function that's constantly processing moves made by players.
        If a player has already been marked as cheater the rule matching will be skipped.
        """
        while True:
            move: Move = self._moves_queue.get()
            player_id = move.player_id
            if player_id in self._cheaters:
                continue

            rule: Rule = self._rules.get(move.hash())
            if not rule:
                raise InvalidMoveConfiguration(type(move), f'Cannot find configuration for {type(move)} move type. Have you configured the cheat engine correclty?. Available types: {self._rules}')

            is_valid_move, msg = rule.evalute(move)
            if not is_valid_move:
                print(f"Player {self._current_player_id} is saying Player {move.player_id} is attempting to cheat - {msg}")
                self._cast_player_cheating_vote(Vote(move=move, value=is_valid_move, accuser_id=self._current_player_id, suspect_id=move.player_id))
            
            time.sleep(self._move_processor_sleep_interval)


    def _cast_player_cheating_vote(self, vote: Vote):
        """
        Called when a player is deemed cheating. 
        Emits an `on_player_cheated` event. Use this to broadcast the result across the network. The event contains the cheater's id.
        """
        self.register_vote(vote)
        self.check_consensus(vote)
        from game.game_state import game_state
        player = game_state.get_player(vote.accuser_id)
        player.vote(vote)

    def check_consensus(self, vote: Vote):
        consensus = (float(len(self._votes[vote.suspect_id])) / float(len(self._player_ids))) * 100
        if consensus > self._consensus_percentage:
            cheater_id = vote.suspect_id
            if cheater_id in self._cheaters:
                return

            print(f"Player {cheater_id} was caught cheating by a majority of {consensus}.")
            self.events.on_player_cheated(cheater_id)
            self._cheaters.append(cheater_id)
