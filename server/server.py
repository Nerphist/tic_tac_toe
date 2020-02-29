from socket import socket, AF_INET, SOCK_STREAM
import logging
import ssl
import sys
import threading
import time
from typing import Optional, List

from server.game import Game
from server.player import Player


class Server:

    def __init__(self):
        # player count for id setting
        self.player_count: int = 1
        self.logger: logging.Logger = self.__form_logger()
        self.server_socket: socket = socket(AF_INET, SOCK_STREAM)
        self.waiting_players: List[Player] = []
        self.context: ssl.SSLContext = self.__create_context()

    def start(self, port: int) -> None:
        """Server start"""
        try:
            self.server_socket.bind(('localhost', port))
            self.server_socket.listen(5)
            self.logger.info('Server started on port ' + str(port))
            self.__handle_clients()
        except OSError as e:
            self.logger.exception(e)
            exit(1)

    def stop(self) -> None:
        """Server stop"""
        self.logger.info('Server stopped')
        self.server_socket.close()

    def __handle_clients(self) -> None:
        """Accepting client connections and starting client threads"""
        while True:
            connection, client_address = self.server_socket.accept()
            self.logger.info(str(client_address) + ' connected')
            connection = self.__get_ssl_socket(connection)

            # creating player and adding him to waiting list
            new_player = Player(connection, self.logger, self.player_count)
            self.player_count += 1
            self.waiting_players.append(new_player)

            threading.Thread(target=self.__client_thread, args=(new_player,)).start()

    def __client_thread(self, player: Player) -> None:
        """Thread for handling a single client"""
        player.send('id_confirm', str(player.id))
        opponent = None
        # looking for opponent
        while not opponent:
            opponent = self.__search_opponent(player)
            if opponent is None:
                time.sleep(1)
                # if player is no more waiting finish this loop
                if player not in self.waiting_players:
                    player = None
                    break
                continue
            # removing player and his opponent from the waiting list
            self.waiting_players.remove(player)
            self.waiting_players.remove(opponent)
            break
        if player:
            # starting a new game
            new_game = Game(self.logger, player, opponent)
            try:
                new_game.start()
            except Exception as e:
                self.logger.error('Game {} vs {} finished by error'.format(player.id, opponent.id))

    def __search_opponent(self, player: Player) -> Optional[Player]:
        """Looking for a free player"""
        for waiter in self.waiting_players:
            if not waiter.opponent and waiter is not player:
                return waiter

    def __form_logger(self) -> logging.Logger:
        """Forming logger to handle server information"""
        log_format = '%(asctime)s - %(levelname)s - %(module)s:%(lineno)s - %(message)s'
        formatter = logging.Formatter(log_format)

        handler1 = logging.FileHandler('logs.txt')
        handler1.setLevel(logging.DEBUG)
        handler1.setFormatter(formatter)

        handler2 = logging.StreamHandler(sys.stdout)
        handler2.setLevel(logging.DEBUG)
        handler2.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        logger.addHandler(handler1)
        logger.addHandler(handler2)
        return logger

    def __create_context(self) -> ssl.SSLContext:
        """Making SSL context for furthering socket wrapping"""
        server_cert = 'cert/server.cert'
        server_key = 'cert/server.key'
        client_certs = 'cert/client.cert'

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_cert_chain(certfile=server_cert, keyfile=server_key)
        context.load_verify_locations(cafile=client_certs)
        return context

    def __get_ssl_socket(self, connection: socket) -> ssl.SSLSocket:
        return self.context.wrap_socket(connection, server_side=True)
