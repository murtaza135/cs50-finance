#!flask/bin/python

import os, sys

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, symbols_request

import random, json, requests

# Configure application
app = Flask(__name__)
app.secret_key = "flash message"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear() ### NOTE: session.clear() breaks message flashing on redirect as the message flash is added to the session object. If you want to flash a message using redirect, make sure there is no session.clear that the code runs through for your message flash to be successful

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash(u"Must provide username", "danger")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash(u"Must provide password", "danger")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=(request.form.get("username")).lower())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash(u"Invalid username and/or password", "danger")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        flash(u"You have successfully logged in", "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash(u"You have successfully logged out", "success")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash(u"Must provide username", "danger")
            return redirect("/register")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash(u"Must provide password", "danger")
            return redirect("/register")

        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            flash(u"Must provide password", "danger")
            return redirect("/register")

        # Ensure "password" & "confirmation" matches
        elif request.form.get("password") != request.form.get("confirmation"):
            flash(u"Passwords do not match! Please re-enter your password", "danger")
            return redirect("/register")

        # Hash password
        hash_password = generate_password_hash(request.form.get("password"))

        # Check if username already exists in database
        user_data = db.execute("SELECT * FROM users WHERE username = :username", username=(request.form.get("username")).lower())

        if user_data:
            flash(u"Username is Already Taken", "danger")
            return redirect("/register")

        # Insert username & password into database, and retrieve unique user id
        user_id = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=(request.form.get("username")).lower(), hash=hash_password)

        # Remember which user has logged in
        session["user_id"] = user_id

        # Redirect user to home page
        flash(u"You have successfully registered an account", "success")
        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            flash(u"Must provide stock symbol", "danger")
            return redirect("/quote")

        # Lookup quote
        quote = lookup(request.form.get("symbol"))
        if not quote:
            flash(u"Must provide a valid stock symbol", "danger")
            return redirect("/quote")

        # Display quote
        return render_template("quoted.html", name=quote["name"], symbol=quote["symbol"], price=usd(quote["price"]))


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Request all symbols from api
        symbols_request()

        # render template
        return render_template("quote.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure stock symbol was submitted
        if not request.form.get("symbol"):
            flash(u"Must provide stock symbol", "danger")
            return redirect("/buy")
        else:
            # Ensure submitted stock symbol exists
            stock = lookup(request.form.get("symbol"))
            if not stock:
                flash(u"Must provide valid stock symbol", "danger")
                return redirect("/buy")

        # Ensure number of shares was submitted
        if not request.form.get("shares"):
            flash(u"Must provide number of shares", "danger")
            return redirect("/buy")

        # Ensure number of shares is an integer
        try:
            num_shares = int(request.form.get("shares"))
        except (TypeError, ValueError):
            flash(u"Must provide valid number of shares", "danger")
            return redirect("/buy")

        # Ensure number of shares is a POSITIVE integer
        if num_shares <= 0:
            flash(u"Must provide valid number of shares", "danger")
            return redirect("/buy")

        # If user has enough cash, then subtract the total cost of the shares he bought from cash
        user_cash = db.execute("SELECT cash FROM users WHERE user_id = :id", id=session["user_id"])
        if len(user_cash) != 1:
            flash(u"Error", "danger")
            return redirect("/buy")

        try:
            user_cash[0]["cash"] = float(user_cash[0]["cash"])
        except TypeError:
            flash(u"Not enough available cash", "danger")
            return redirect("/buy")

        if user_cash[0]["cash"] > stock["price"] * num_shares:
            new_cash = user_cash[0]["cash"] - (stock["price"] * num_shares)
            db.execute("UPDATE users SET cash = :cash WHERE user_id = :id", cash=new_cash, id=session["user_id"])
        else:
            flash(u"Not enough available cash", "danger")
            return redirect("/buy")

        # Store the details of this purchase into the "history" table
        db.execute("INSERT INTO history (user_id, symbol, price, shares, difference) VALUES (:user_id, :symbol, :price, :shares, :difference)",
                    user_id=session["user_id"], symbol=(request.form.get("symbol")).upper(), price=stock["price"], shares=num_shares, difference=stock["price"] * num_shares)

        # Update the user's details regarding how many shares he has for each stock
        stock_data = db.execute("SELECT * FROM stocks WHERE user_id = :id AND symbol = :symbol",
                                id=session["user_id"], symbol=(request.form.get("symbol")).upper())

        if not stock_data:
            # If current stock has not EVER been purchased by user, then create a new stock
            db.execute("INSERT INTO stocks (user_id, symbol, shares) VALUES (:user_id, :symbol, :shares)",
                        user_id=session["user_id"], symbol=(request.form.get("symbol")).upper(), shares=num_shares)

        elif len(stock_data) == 1:
            # else update the current stock
            db.execute("UPDATE stocks SET shares = :shares WHERE data_id = :id",
                        shares=num_shares+stock_data[0]["shares"], id=stock_data[0]["data_id"])

        else:
            flash(u"Error", "danger")
            return redirect("/buy")


        # Redirect to "index.html"
        flash(u"You have successfully bought {} shares".format(num_shares), "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Request all symbols from api
        symbols_request()

        # render template
        return render_template("buy.html")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Retrieve cash from database
    total_cash = db.execute("SELECT cash FROM users where user_id=:id", id=session["user_id"])
    if len(total_cash) != 1:
        return apology("Error", 400)


    # Retrieve stocks (symbol & shares) of user from database
    stock_data = db.execute("SELECT symbol, shares FROM stocks WHERE user_id = :id ORDER BY symbol", id=session["user_id"])

    # if there is no stock_data present, then present an empty table and present the total cash value retrieved in the previous lines of code
    if not stock_data:
        user_data = {
            "symbol": None,
            "name": None,
            "price": None,
            "shares": None,
            "stock_value": None
        }

        return render_template("index.html", user_data=user_data, total_cash=usd(total_cash[0]["cash"]), grand_total=usd(total_cash[0]["cash"]), data_available=False)


    # else: collate data for table
    else:
        # Initiliase list of stocks with it's data and initialise grand_total, which will be calculated within the coming loop
        user_data = []
        grand_total = total_cash[0]["cash"]

        for stock in stock_data:
            # Look up price for selected symbol
            quote = lookup(stock["symbol"])

            # calculate total_price of each stock (i.e current price of stock * number of shares)
            stock_value = quote["price"] * stock["shares"]

            # Add stock_value to grand_total
            grand_total += stock_value

            # Collate data
            collated_data = {
                "symbol": stock["symbol"],
                "name": quote["name"],
                "price": usd(quote["price"]),
                "shares": stock["shares"],
                "stock_value": usd(stock_value)
            }

            # Append to user_data
            user_data.append(collated_data)


        # Render_template index
        return render_template("index.html", user_data=user_data, total_cash=usd(total_cash[0]["cash"]), grand_total=usd(grand_total), data_available=True)




@app.route("/buy_stock", methods=["GET"])
@app.route("/buy_stock/<string:symbol>", methods=["GET", "POST"])
@login_required
def index_buy(symbol=""):
    """ Buy shares of stock through index """

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # lookup submitted stock symbol
        stock = lookup(symbol)
        if not stock:
            flash(u"Must provide valid stock symbol", "danger")
            return redirect("/")

        # Ensure number of shares was submitted
        if not request.form.get("shares"):
            flash(u"Must provide number of shares", "danger")
            return redirect("/")

        # Ensure number of shares is an integer
        try:
            num_shares = int(request.form.get("shares"))
        except (TypeError, ValueError):
            flash(u"Must provide valid number of shares", "danger")
            return redirect("/")

        # Ensure number of shares is a POSITIVE integer
        if num_shares <= 0:
            flash(u"Must provide valid number of shares", "danger")
            return redirect("/")

        # If user has enough cash, then subtract the total cost of the shares he bought from cash
        user_cash = db.execute("SELECT cash FROM users WHERE user_id = :id", id=session["user_id"])
        if len(user_cash) != 1:
            flash(u"Error", "danger")
            return redirect("/")

        try:
            user_cash[0]["cash"] = float(user_cash[0]["cash"])
        except TypeError:
            flash(u"Not enough available cash", "danger")
            return redirect("/")

        if user_cash[0]["cash"] > stock["price"] * num_shares:
            new_cash = user_cash[0]["cash"] - (stock["price"] * num_shares)
            db.execute("UPDATE users SET cash = :cash WHERE user_id = :id", cash=new_cash, id=session["user_id"])
        else:
            flash(u"Not enough available cash", "danger")
            return redirect("/")

        # Store the details of this purchase into the "history" table
        db.execute("INSERT INTO history (user_id, symbol, price, shares, difference) VALUES (:user_id, :symbol, :price, :shares, :difference)",
                    user_id=session["user_id"], symbol=symbol.upper(), price=stock["price"], shares=num_shares, difference=stock["price"] * num_shares)

        # Update the user's details regarding how many shares he has for each stock
        stock_data = db.execute("SELECT * FROM stocks WHERE user_id = :id AND symbol = :symbol",
                                id=session["user_id"], symbol=symbol.upper())

        if not stock_data:
            # If current stock has not EVER been purchased by user, then create a new stock
            db.execute("INSERT INTO stocks (user_id, symbol, shares) VALUES (:user_id, :symbol, :shares)",
                        user_id=session["user_id"], symbol=symbol.upper(), shares=num_shares)

        elif len(stock_data) == 1:
            # else update the current stock
            db.execute("UPDATE stocks SET shares = :shares WHERE data_id = :id",
                        shares=num_shares+stock_data[0]["shares"], id=stock_data[0]["data_id"])

        # redirect to index
        if num_shares == 1:
            flash(u"You have successfully bought 1 share", "success")
        elif num_shares > 1:
            flash(u"You have successfully bought {} shares".format(num_shares), "success")

        return redirect("/")


    # User reached route via GET
    else:
        return redirect("/")


@app.route("/sell_stock", methods=["GET"])
@app.route("/sell_stock/<string:symbol>", methods=["GET", "POST"])
@login_required
def index_sell(symbol=""):
    """ Sell shares of stock through index """

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check if the user actually owns any of that stock
        symbols_in_database = db.execute("SELECT symbol FROM stocks WHERE user_id=:id", id=session["user_id"])

        stock_present = False
        for symbol_in_database in symbols_in_database:
            if symbol_in_database["symbol"] == symbol:
                stock_present = True
                break

        if stock_present == False:
            flash(u"You do not have enough of that stock available", "danger")
            return redirect("/")

        # Ensure number of shares was submitted
        if not request.form.get("shares"):
            flash(u"Must provide number of shares", "danger")
            return redirect("/")

        # Ensure number of shares is an integer
        try:
            num_shares = int(request.form.get("shares"))
        except (TypeError, ValueError):
            flash(u"Must provide valid number of shares", "danger")
            return redirect("/")

        # Ensure number of shares is a POSITIVE integer
        if num_shares <= 0:
            flash(u"Must provide valid number of shares", "danger")
            return redirect("/")

        # Check if user has bought more shares than he is selling
        already_bought_shares = db.execute("SELECT shares FROM stocks WHERE user_id = :id AND symbol = :symbol",
                                    id=session["user_id"], symbol=symbol.upper())

        if len(already_bought_shares) != 1:
            flash(u"Error", "danger")
            return redirect("/")


        if num_shares <= 0 or num_shares > already_bought_shares[0]["shares"]:
            flash(u"Must provide valid number of shares", "danger")
            return redirect("/")


        # Update cash
        quote = lookup(symbol)
        user_cash = db.execute("SELECT cash FROM users WHERE user_id = :id", id=session["user_id"])

        new_cash = user_cash[0]["cash"] + (quote["price"] * num_shares)
        db.execute("UPDATE users SET cash = :cash WHERE user_id = :id", cash=new_cash, id=session["user_id"])

        # Update history
        db.execute("INSERT INTO history (user_id, symbol, price, shares, difference) VALUES (:user_id, :symbol, :price, :shares, :difference)",
                    user_id=session["user_id"], symbol=symbol.upper(), price=quote["price"], shares=0-num_shares, difference=quote["price"] * num_shares)

        # Sell shares and update user's stocks details
        if already_bought_shares[0]["shares"] - num_shares > 0:
            db.execute("UPDATE stocks SET shares = :shares WHERE user_id = :id AND symbol = :symbol",
                        shares=already_bought_shares[0]["shares"] - num_shares, id=session["user_id"], symbol=symbol.upper())
        else:
            db.execute("DELETE FROM stocks WHERE user_id = :id AND symbol = :symbol", id=session["user_id"], symbol=symbol.upper())


        # Redirect to "index.html"
        if num_shares == 1:
            flash(u"You have successfully sold 1 share", "success")
        elif num_shares > 1:
            flash(u"You have successfully sold {} shares".format(num_shares), "success")

        return redirect("/")


    # User reached route via GET
    else:
        return redirect("/")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check if user has selected a symbol
        if not request.form.get("symbol"):
            flash(u"Please select a symbol", "danger")
            return redirect("/sell")

        # Check if the user actually owns any of that stock
        symbols = db.execute("SELECT symbol FROM stocks WHERE user_id=:id", id=session["user_id"])

        stock_present = False
        for symbol in symbols:
            if symbol["symbol"] == (request.form.get("symbol")).upper():
                stock_present = True
                break

        if stock_present == False:
            flash(u"You do not have enough of that stock available", "danger")
            return redirect("/sell")


        # Check if user has entered a number of shares
        if not request.form.get("shares"):
            flash(u"Please enter number of shares", "danger")
            return redirect("/sell")

        # Ensure number of shares is an integer
        try:
            num_shares = int(request.form.get("shares"))
        except TypeError:
            flash(u"Must provide valid number of shares", "danger")
            return redirect("/sell")

        # Check if user has bought more shares than he is selling
        already_bought_shares = db.execute("SELECT shares FROM stocks WHERE user_id = :id AND symbol = :symbol",
                                    id=session["user_id"], symbol=(request.form.get("symbol")).upper())

        if len(already_bought_shares) != 1:
            flash(u"Error", "danger")
            return redirect("/sell")


        if num_shares <= 0 or num_shares > already_bought_shares[0]["shares"]:
            flash(u"You do not have enough shares!", "danger")
            return redirect("/sell")


        # Update cash
        quote = lookup(request.form.get("symbol"))
        user_cash = db.execute("SELECT cash FROM users WHERE user_id = :id", id=session["user_id"])

        new_cash = user_cash[0]["cash"] + (quote["price"] * num_shares)
        db.execute("UPDATE users SET cash = :cash WHERE user_id = :id", cash=new_cash, id=session["user_id"])

        # Update history
        db.execute("INSERT INTO history (user_id, symbol, price, shares, difference) VALUES (:user_id, :symbol, :price, :shares, :difference)",
                    user_id=session["user_id"], symbol=(request.form.get("symbol")).upper(), price=quote["price"], shares=0-num_shares, difference=quote["price"] * num_shares)

        # Sell shares and update user's stocks details
        if already_bought_shares[0]["shares"] - num_shares > 0:
            db.execute("UPDATE stocks SET shares = :shares WHERE user_id = :id AND symbol = :symbol",
                        shares=already_bought_shares[0]["shares"] - num_shares, id=session["user_id"], symbol=(request.form.get("symbol")).upper())
        else:
            db.execute("DELETE FROM stocks WHERE user_id = :id AND symbol = :symbol", id=session["user_id"], symbol=(request.form.get("symbol")).upper())


        # Redirect to "index.html"
        flash(u"You have successfully sold {} shares".format(num_shares), "success")
        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # retrieve symbols whose shares the user has bought from the database
        symbols = db.execute("SELECT symbol FROM stocks WHERE user_id = :id", id=session["user_id"])

        # render template
        return render_template("sell.html", symbols=symbols)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Retrieve data from user history
    user_data = db.execute("SELECT symbol, price, shares, difference, timestamp FROM history WHERE user_id = :id ORDER BY timestamp DESC", id=session["user_id"])

    for data in user_data:
        data["price"] = usd(data["price"])
        data["difference"] = usd(data["difference"])

    # Render template
    return render_template("history.html", user_data=user_data)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    "Change user password"

    # User reached route via POST (as by submitting a form via POST)
    if request.method=="POST":

        # Check if old password has been entered
        if not request.form.get("old_password"):
            flash(u"Please enter your old password", "danger")
            return redirect("/change_password")

        # Check if old password matches their current password in the database
        current_password = db.execute("SELECT hash FROM users WHERE user_id = :id", id=session["user_id"])
        if len(current_password) != 1 or not check_password_hash(current_password[0]["hash"], request.form.get("old_password")):
            flash(u"The old password you mentioned does not match your current password", "danger")
            return redirect("/change_password")

        # Check if new password has been entered
        if not request.form.get("new_password"):
            flash(u"Please enter your new password", "danger")
            return redirect("/change_password")

        # Check if confirmation has been entered
        if not request.form.get("confirmation"):
            flash(u"Please confirm your new password", "danger")
            return redirect("/change_password")

        # Check if new password and confirmation match
        if request.form.get("new_password") != request.form.get("confirmation"):
            flash(u"Your passwords do not match", "danger")
            return redirect("/change_password")

        # Insert new HASHED password into database
        hash_password = generate_password_hash(request.form.get("new_password"))
        db.execute("UPDATE users SET hash = :hash WHERE user_id = :id", hash=hash_password, id=session["user_id"])

        # Redirect user to home page
        flash(u"You have successfully changed your password", "success")
        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change_password.html")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    "Delete account"

    # User reached route via POST (as by submitting a form via POST)
    if request.method=="POST":

        # check if password has been entered
        if not request.form.get("password"):
            flash(u"Please enter your password", "danger")
            return redirect("/delete")

        # check if confirmation has been entered
        if not request.form.get("confirmation"):
            flash(u"Please confirm your password", "danger")
            return redirect("/delete")

        # check if passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            flash(u"Your passwords do not match! Please re-enter your password", "danger")
            return redirect("/delete")

        # check if password matches the password in the database
        database_password = db.execute("SELECT hash FROM users where user_id=:id", id=session["user_id"])
        if len(database_password) != 1 or not check_password_hash(database_password[0]["hash"], request.form.get("password")):
            flash(u"You have entered the incorrect password, please try again", "danger")
            return redirect("/delete")

        # delete data from table (users, stocks) and update table (history) with data of the account deletion
        users_data = db.execute("SELECT * FROM users where user_id=:id", id=session["user_id"])
        if len(users_data) != 1:
            flash(u"Error", "Danger")
            return redirect("/delete")

        grand_total = users_data[0]["cash"]
        db.execute("DELETE FROM users WHERE user_id=:id", id=session["user_id"])

        stock_data = db.execute("SELECT * FROM stocks WHERE user_id=:id", id=session["user_id"])
        if len(stock_data) == 1:
            db.execute("DELETE FROM stocks WHERE user_id=:id", id=session["user_id"])

            for stock in stock_data:
                data = lookup(stock["symbol"])
                grand_total += (data["price"] * stock["shares"])


        db.execute("INSERT INTO history (user_id, symbol, price, shares, difference) VALUES (:user_id, :symbol, :price, :shares, :difference)",
                    user_id=session["user_id"], symbol="DELETE", price=0-grand_total, shares=0, difference=grand_total)


        # clear session and redirect to login
        session.clear()

        flash(u"You have successfully deleted your account", "success")
        return render_template("login.html")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("delete.html")


@app.route("/register_username_hint", methods=["GET"])
def receive():
    """ alert user if currently typed username is available or not """

    # receive data from AJAX and put it into data
    data = request.args.get("username", type=str)

    # Query database to see if currently written username is available or not
    database_usernames = db.execute("SELECT username FROM users WHERE username=:username;", username=data)

    # return JSON object based on whether username is available or not
    if len(database_usernames) == 0:
        return jsonify(message = "Username is available")
    else:
        return jsonify(message = "Username is not available")


@app.route("/index_price_refresh", methods=["GET"])
#@login_required
def index_price_refresh():
    """ refresh all prices on index every 30 minutes """

    # receive data from AJAX and put it into data
    data = request.args.get("symbol", type=str)

    # Lookup the symbol received from AJAX
    symbol_data = lookup(data)

    # return price of symbol to be updated on index
    return jsonify(price = usd(symbol_data["price"]))


@app.route("/symbol_search_filter", methods=["GET"])
@login_required
def symbol_search_filter():
    """ return a list of 10 symbols which can be used to complete the search box value """

    # receive data from AJAX and put it into data
    data = request.args.get("search_box_value", type=str)
    data_length = len(data)

    # open "symbols.txt", read symbols and place them into a list of dictionaries
    with open("symbols.txt", "r") as symbols_file:
        symbols = [dict(symbol=line[:-1]) for line in symbols_file]

    # Compare symbols with data, and remove any symbols which do not match
    removed = 0
    for i in range(len(symbols)):
        symbol = symbols[i-removed]["symbol"]
        if (symbol[:data_length]).upper() != data.upper():
            symbols.pop(i-removed)
            removed += 1

    # return list of symbols
    if len(symbols) >= 10:
        return jsonify(symbols[:10])
    else:
        return jsonify(symbols)




def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


# Run application through the compiler "python" as oposed to "flask run"
if __name__ == '__main__':
	app.run()
