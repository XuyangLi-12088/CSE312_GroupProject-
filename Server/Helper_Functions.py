import socketserver


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        retrieved = self.request.recv(2048).strip().decode().lower()


# <----------------------------> #
# Return HTML, CSS & JS if there #
# <----------------------------> #
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


def login():
    HTML = "HTTP/1.1 200 OK\r\n" \
           "X-Content-Type-Options: nosniff" \
           "\r\nContent-Type: text/html; charset=UTF-8" \
           "\r\nContent-Length: {}\r\n\r\n{}".format(len(read("Server/Styles/login.html")),
                                                     read("Server/Styles/login.html")).encode()
    return HTML


def css():
    CSS = "HTTP/1.1 200 OK\r\n" \
          "X-Content-Type-Options: nosniff" \
          "\r\nContent-Type: text/css; charset=UTF-8" \
          "\r\nContent-Length: {}\r\n\r\n{}".format(len(read("Server/Styles/Background.css")),
                                                    read("Server/Styles/Background.css")).encode()
    return CSS


def get_header(data):
    data = data.split(' ')
    header = data[0] + data[1]
    return header


def respond_200(code, options, types, length):
    data = "HTTP/1.1 " + code + "\r\n" \
           "X-Content-Type_Options: " + options + "\r\n" \
           "Content_Type: " + types + "charset=UTF-8" + "\r\n" \
           "Content-Length: " + length + "\r\n\r\n"
    return data


def respond_301(location):
    data = ("HTTP/1.1 301 Moved Permanently\r\n"
            "Content-Length: 0\r\nLocation: " + location + "\r\n\r\n").encode()

