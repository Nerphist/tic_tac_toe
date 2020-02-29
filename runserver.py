from server.server import Server

if __name__ == '__main__':
    server = Server()
    server.start(30000)
    server.stop()
