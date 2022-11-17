

def escape_html(input):
    return input.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")