import random
from logging import Logger
from typing import List, Set, Union

from server.player import Player


class Game:
    """Game class describes a game with two different players."""

    def __init__(self, logger: Logger, player1: Player, player2: Player):
        self.logger: Logger = logger
        players: List[Player] = [player1, player2]
        random.shuffle(players)
        self.player1, self.player2 = tuple(players)
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1
        self.player1.role = 'X'
        self.player2.role = 'O'
        self.board_content: List[str] = list(' ' * 9)
        self.moving_player: Player = player1
        self.result: int = -1

    def start(self) -> None:
        """Starting game and performing game logic"""
        self.logger.info('Game {} vs {} started'.format(self.player1.id, self.player2.id))

        # sending players info
        self.player1.send_personal_info()
        self.player2.send_personal_info()

        while self.result == -1:
            # waiting for players to move before game is finished
            self.__move()
            # checking if game is finished
            self.result = self.__check_board(self.moving_player)
            if self.result == -1:
                # changing the moving player
                self.moving_player = self.moving_player.opponent
        # sending result after the end
        self.__send_result()

    def __move(self) -> None:
        """Move logic """

        # sending board and turn to both players
        self.moving_player.send('board', ("".join(self.board_content)))
        self.moving_player.opponent.send('board', ("".join(self.board_content)))

        self.moving_player.send('turn_possible', 'true')
        self.moving_player.opponent.send('turn_possible', 'false')

        # waiting for moving player to send a move_id and sending it back to his opponent
        move = int(self.moving_player.get_message('move_id'))
        self.moving_player.opponent.send('move_id', str(move))
        if self.board_content[move] == ' ':
            self.board_content[move] = self.moving_player.role

    def __check_board(self, player: Player) -> int:
        """Checking if there are winning combinations"""
        if ' ' not in self.board_content:
            return 0
        winning_combos: Set[str] = {'123', '456', '789', '147', '258', '369', '159', '357'}
        filled_squares = {str(i) for i, square in enumerate(self.board_content, 1) if square == player.role}
        for combo in winning_combos:
            if set(combo).issubset(filled_squares):
                return 1
        return -1

    def __send_result(self) -> None:
        """Sending game result to both players"""
        self.moving_player.send('board', ("".join(self.board_content)))
        self.moving_player.opponent.send('board', ("".join(self.board_content)))

        if self.result == 0:
            self.player1.send('game_result', 'It\'s a draw')
            self.player2.send('game_result', 'It\'s a draw')
            self.logger.info('Game {} vs {} finished by a draw'.format(self.player1.id, self.player2.id))
        if self.result == 1:
            self.moving_player.send('game_result', 'You win!')
            self.moving_player.opponent.send('game_result', 'You lose')
            self.logger.info('Game {} vs {} finished by {} victory'.format(self.player1.id, self.player2.id,
                                                                           self.moving_player.id))
