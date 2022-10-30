import socketserver
import Server.Helper_Functions as HelpFunc


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # TODO Work in Progress!
        retrieved = self.request.recv(2048).strip().decode().lower()
        header = HelpFunc.get_header(retrieved)
        if header == "get/":
            data = "HTTP/1.1 301 Moved Permanently\r\n" \
                   "Content-Length: 0\r\nLocation: http://localhost:8080/login\r\n\r\n".encode()
            self.request.sendall(data)

        elif header == "get/background.css":
            self.request.sendall(HelpFunc.css())

        elif header == "get/login":
            self.request.sendall(HelpFunc.login())

        else:
            self.request.sendall(
                "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 31\r\n\r\n There is no content "
                "to be shown".encode()
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
    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()
