"""urllib utilities."""
from urllib.request import HTTPRedirectHandler


class CustomHTTPRedirectHandler(HTTPRedirectHandler):
    """Custom HTTPRedirectHandler with a greater number of max allowable redirections."""

    max_redirections = 20
