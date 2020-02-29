from tkinter import *

from client.client_service import ClientService


class ClientUI:

    def __init__(self):
        self.tk = Tk()
        self.tk.title("Tic Tac Toe")
        self.tk.protocol("WM_DELETE_WINDOW", self.finish_game)
        self.service = ClientService()

        self.service.my_label = Label(self.tk, text="You:", font='Times 20 bold', bg='white', fg='black', height=1,
                                      width=8)
        self.service.my_label.grid(row=1, column=1, columnspan=1)

        self.service.opponent_label = Label(self.tk, text="Opponent:", font='Times 20 bold', bg='white', fg='black',
                                            height=1, width=16)
        self.service.opponent_label.grid(row=1, column=2, columnspan=2)

        self.service.buttons = [
            Button(self.tk, text=' ', font='Times 20 bold', bg='gray', fg='white', height=4, width=8, ) for
            i in range(3 ** 2)]
        for i, button in enumerate(self.service.buttons):
            # binding lambda function to every button
            button.configure(command=lambda current=button: self.click_button(current))
            button.grid(row=i // 3 + 3, column=i % 3 + 1)

        self.service.status_bar = Label(self.tk, text="Waiting for start", font='Times 20 bold', bg='white', fg='black',
                                        height=1, width=16)
        self.service.status_bar.grid(row=6, column=1, columnspan=3)

        restart_button = Button(self.tk, text='Restart', font='Times 20 bold', bg='gray', fg='white', height=2,
                                width=8, command=self.restart)
        restart_button.grid(row=7, column=1, columnspan=2)

        quit_button = Button(self.tk, text='Quit', font='Times 20 bold', bg='gray', fg='white', height=2,
                             width=8, command=self.finish_game)
        quit_button.grid(row=7, column=2, columnspan=8)

    def click_button(self, button: Button) -> None:
        self.service.make_move(button)

    def finish_game(self) -> None:
        self.service.close()
        self.tk.quit()

    def restart(self) -> None:
        self.service.restart()

    def start_game(self) -> None:
        self.service.start()
