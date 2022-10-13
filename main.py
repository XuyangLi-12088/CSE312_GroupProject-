import socketserver
import Server.Helper_Functions as HelpFunc


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # TODO Work in Progress!
        retrieved = self.request.recv(2048).strip().decode().lower()
        home = HelpFunc.homepage()  # Loads the HTML
        css = HelpFunc.css()        # Loads the CSS
        if "get / " in retrieved:
            self.request.sendall(home)
        elif ".css" in retrieved:
            self.request.sendall(css)
        else:
            self.request.sendall(
                "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 31\r\n\r\n There is no content to be shown".encode()
            )


if __name__ == "__main__":
    # <----------------------------------------> #
    # to host locally instead of docker
    host = "localhost"
    port = 8080
    # <----------------------------------------> #
    # docker-compose up --build --force-recreate
    # host = "0.0.0.0"
    # port = 8000
    server = socketserver.TCPServer((host, port), MyTCPHandler)
    server.serve_forever()
