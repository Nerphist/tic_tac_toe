import json
from logging import Logger
from socket import socket
from typing import Optional


class Player:
    def __init__(self, connection: socket, logger: Logger, player_id: int):
        self.logger = logger
        self.id = player_id
        self.connection = connection
        self.opponent: Optional[Player] = None
        self.role: Optional[str] = None

    def send(self, command: str, message: str) -> None:
        try:
            self.connection.send(self.__form_message(command, message))
        except OSError:
            self.__disconnect()

    def get_message(self, expected_type) -> Optional[str]:
        try:
            msg = json.loads(self.connection.recv(256).decode())
            if msg['command'] == 'exit' or msg['command'] != expected_type:
                self.__disconnect()
            else:
                return msg['message']
        except ConnectionAbortedError:
            self.__disconnect()
        except ConnectionResetError:
            self.__disconnect()
        return None

    def send_personal_info(self):
        self.send('role', self.role)
        self.send('opponent', str(self.opponent.id))

    def __disconnect(self):
        self.logger.info('Player {} disconnected'.format(self.id))
        if self.opponent:
            try:
                self.opponent.send('quit', '')
            except OSError as e:
                self.logger.exception(e)
        raise Exception('Finish thread')

    def __form_message(self, command: str, message: str):
        return (json.dumps({
            'command': command,
            'message': message
        }) + '\n').encode('utf-8')
