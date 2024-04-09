import requests
import urllib.parse
import json

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        response = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/quote")
        response.raise_for_status() # checks if request was successful
    except requests.RequestException: # any exception that arises (i.e the request failed), then return none
        return None

    # Parse response
    try:
        quote = response.json() # decode json object into a python dictionary and put it into quote for it to be manipulated in the next few lines
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def symbols_request():
    """ Request all symbols from api and save it to external file """

    # Contact API
    try:
        response = requests.get("https://api.iextrading.com/1.0/ref-data/symbols")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        symbols = response.json()
    except (KeyError, TypeError, ValueError):
        return None

    # Save to external file
    with open("symbols.txt", "w") as outputFile:
        for symbol in symbols:
            outputFile.write(symbol['symbol'] + '\n')


def usd(value):
    """Format value as USD."""

    return f"${value:,.2f}"