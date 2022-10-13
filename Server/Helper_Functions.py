import socketserver

class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        retrieved = self.request.recv(2048).strip().decode().lower()

# <----------------------------> #
# Return HTML, CSS & JS if there #
# <----------------------------> #
def homepage():
    HTML = "HTTP/1.1 200 OK\r\n" \
           "X-Content-Type-Options: nosniff" \
           "\r\nContent-Type: text/html; charset=UTF-8" \
           "\r\nContent-Length: {}\r\n\r\n{}".format(len(read("Server/Styles/App_Layout.html")), read("Server/Styles/App_Layout.html")).encode()
    return HTML

def css():
    CSS = "HTTP/1.1 200 OK\r\n" \
          "X-Content-Type-Options: nosniff" \
          "\r\nContent-Type: text/css; charset=UTF-8" \
          "\r\nContent-Length: {}\r\n\r\n{}".format(
        len(read("Server/Styles/Background.css")),read("Server/Styles/Background.css")).encode()
    return CSS

# <-------> #
# Read File #
# <-------> #
def read(filename):
    retVal = ''
    with open(filename, "rb") as f:
        lines = f.readlines()
    idx = [line.decode('utf-8') for line in lines]
    for ele in idx:
        retVal += ' ' + ele
    return retVal
