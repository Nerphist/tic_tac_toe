import json
import ssl
import traceback
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from tkinter import Button, Label
from typing import Tuple, Optional, List, Dict


class ClientService:

    def __init__(self):
        self.address: Tuple[str, int] = ('localhost', 30000)
        # player id
        self.id: Optional[int] = None
        # sign of player
        self.role: Optional[str] = None
        # opponent id
        self.opponent: Optional[int] = None
        # ui elements
        self.buttons: Optional[List[Button]] = None
        self.my_label: Optional[Label] = None
        self.opponent_label: Optional[Label] = None
        self.status_bar: Optional[Label] = None

        self.turn_possible: Optional[bool] = False
        self.game_finished: bool = False
        self.connected: bool = False
        # dictionary where keys are commands of the server and values are functions which process them
        self.processing_dict: Dict[str, callable] = {
            'id_confirm': self.__process_id,
            'role': self.__process_role,
            'opponent': self.__process_opponent,
            'board': self.__process_board,
            'turn_possible': self.__process_turn_possible,
            'move_id': self.__process_move_made,
            'game_result': self.__process_game_result,
            'quit': self.__process_quit,
        }
        self.client_socket: ssl.SSLSocket = self.__get_ssl_socket()

    def start(self) -> None:
        """Starting the client and connecting the server"""
        self.__connect(self.address)
        self.game_finished = False
        self.my_label['text'] = 'You:'
        self.opponent_label['text'] = 'Opponent:'
        self.status_bar['text'] = 'Waiting for start'
        # starting communication thread
        receive_thread = Thread(target=self.__receive)
        receive_thread.start()

    def close(self) -> None:
        """Closing the connection"""
        try:
            self.__send('exit')
            self.game_finished = True
            self.client_socket.close()
        except OSError:
            traceback.print_exc()

    def restart(self) -> None:
        """Closing the connection and starting a new one"""
        if self.game_finished:
            self.__reload_game()
            self.close()
            self.client_socket = self.__get_ssl_socket()
            self.connected = False
            self.start()

    def make_move(self, button: Button) -> None:
        """Making a move and sending it to the server"""
        if self.turn_possible and button['text'] == ' ':
            button['text'] = self.role
            self.__send('move_id', str(self.buttons.index(button)))
            self.turn_possible = False

    def __connect(self, address: Tuple[str, int]) -> None:
        """Server connection"""
        while not self.connected:
            # trying to connect to the server until its started
            try:
                self.client_socket.connect(address)
                self.connected = True
            except ConnectionRefusedError:
                print('Waiting for server to startup...')

    def __reload_game(self) -> None:
        """Cleaning the client information"""
        self.turn_possible = False
        self.opponent = None
        self.my_label['text'] = 'You:'
        self.opponent_label['text'] = 'Opponent:'
        for b in self.buttons:
            b['text'] = ' '
        self.role = None

    def __receive(self) -> None:
        """Thread target to receive commands from server and send commands back"""
        while not self.game_finished:
            try:
                messages = self.client_socket.recv(1024).decode("utf8")
                # messages are split in case of getting more than one at once
                for message in messages.split('\n')[:-1]:
                    message: dict = json.loads(message)
                    command: str = message['command']
                    message: str = message['message']
                    if command in self.processing_dict:
                        self.processing_dict[command](message)
                    else:
                        print('Unknown command \'{}\' received'.format(command))
            except OSError as e:
                print('Disconnected from the server')
                exit(1)

    def __process_id(self, message: str) -> None:
        self.id = int(message)
        self.my_label['text'] += message

    def __process_role(self, message: str):
        self.role = message

    def __process_opponent(self, message: str):
        self.opponent = int(message)
        self.opponent_label['text'] += message

    def __process_board(self, message: str):
        self.board = [i for i in message]

    def __process_turn_possible(self, message: str) -> None:
        self.turn_possible = message == 'true'
        self.status_bar['text'] = 'Your turn' if self.turn_possible else 'Opponent\'s turn'

    def __process_move_made(self, message: str) -> None:
        move_id = int(message)
        self.buttons[move_id]['text'] = 'X' if self.role == 'O' else 'O'

    def __process_game_result(self, message: str) -> None:
        self.status_bar['text'] = message
        self.opponent = None
        self.game_finished = True

    def __process_quit(self, *args) -> None:
        self.game_finished = True
        self.__reload_game()
        self.status_bar['text'] = 'Opponent left'

    def __send(self, command: str, content: Optional[str] = None) -> None:
        """Sending message back to the server"""
        message = {
            'command': command,
        }
        if content:
            message['message'] = content
        message = self.__form_message(message)
        self.client_socket.send(message)

    def __form_message(self, message_dict: dict) -> bytes:
        return json.dumps(message_dict).encode('utf-8')

    def __get_ssl_socket(self) -> ssl.SSLSocket:
        """SSL wrapper for client socket"""
        client_socket = socket(AF_INET, SOCK_STREAM)

        server_cert = 'cert/server.cert'
        client_cert = 'cert/client.cert'
        client_key = 'cert/client.key'
        return ssl.wrap_socket(client_socket, server_side=False, ssl_version=ssl.PROTOCOL_TLSv1_2, keyfile=client_key,
                               certfile=client_cert, ca_certs=server_cert)
