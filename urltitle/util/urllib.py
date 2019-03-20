from urllib.request import HTTPRedirectHandler


class CustomHTTPRedirectHandler(HTTPRedirectHandler):
    max_redirections = 20
