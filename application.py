import os

from flask import Flask, session, request, render_template, redirect, jsonify, flash

from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

import requests
import helpers


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URI"):
    raise RuntimeError("DATABASE_URI is not set")

# Configure session to use filesystem
app.config['DEBUG'] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URI"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():

    return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":


        if not request.form.get("username"):

            return render_template('error.html', message="must provide username")
        # Query database for username
        userCheck = db.execute("SELECT * FROM users WHERE username = :username",
                               {"username": request.form.get("username")}).fetchone()

        # Check if username already exist
        if userCheck:
            return "username already exist"

        # Ensure password was submitted
        elif not request.form.get("password"):

            return render_template('error.html', message="must provide password")

        # Ensure confirmation wass submitted
        elif not request.form.get("confirmation"):
            return render_template('error.html', message="confirm password")

        # Check passwords are equal
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template('error.html', message="passwords didn't match")

        # Hash user's password to store in DB
        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        # Insert register into DB
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                   {"username": request.form.get("username"),
                    "password": hashedPassword})

        # Commit changes to database
        db.commit()



        # Redirect user to login page
        return "account created"

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Forget any user_id
    session.clear()

    username = request.form.get("username")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template('error.html', message="no username provided")

        # Ensure password was submitted
        elif not request.form.get("password"):

            return render_template('error.html', message="must provide password")

        # Query database for username (http://zetcode.com/db/sqlalchemy/rawsql/)
        # https://docs.sqlalchemy.org/en/latest/core/connections.html#sqlalchemy.engine.ResultProxy
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username})

        result = rows.fetchone()

        # Ensure username exists and password is correct
        if result==None:
            return render_template('error.html', message="invalid username and/or password")
        if not check_password_hash(result[2], request.form.get("password")):
            return render_template('error.html', message="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = result[0]
        session["user_name"] = result[1]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/search", methods=["GET"])
def search():
    """ Get books results """

    # Check book id was provided
    if not request.args.get("book"):
        return "you must provide a book."

    # Take input and add a wildcard
    query = "%" + request.args.get("book") + "%"

    # Capitalize all words of input for search
    # https://docs.python.org/3.7/library/stdtypes.html?highlight=title#str.title
    query = query.title()

    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn LIKE :query OR \
                        title LIKE :query OR \
                        author LIKE :query LIMIT 15",
                      {"query": query})

    # Books not founded
    if rows.rowcount == 0:
        return "we can't find books with that description."

    # Fetch all the results
    books = rows.fetchall()

    return render_template("results.html", books=books)


@app.route("/book/<isbn>", methods=['GET', 'POST'])
@helpers.login_required
def book(isbn):
    """ Save user review and load same page with reviews updated."""

    if request.method == "POST":

        # Save current user info
        currentuser = session["user_id"]

        # Fetch form data
        rating = request.form.get("rating")
        comment = request.form.get("comment")

        # Search book_id by ISBN
        row = db.execute("SELECT isbn FROM books WHERE isbn = :isbn",
                         {"isbn": isbn})

        # Save id into variable
        bookId = row.fetchone()  # (id,)
        bookId = bookId[0]

        # Check for user submission (ONLY 1 review/user allowed per book)
        row2 = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND isbn = isbn",
                          {"user_id": currentuser,
                           "isbn": bookId})

        # A review already exists
        if row2.rowcount != NULL:
            flash('You already submitted a review for this book', 'warning')
            return redirect("/book/" + isbn)

        # Convert to save into DB
        rating = int(rating)

        db.execute("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES \
                    (:user_id, :book_id, :comment, :rating)",
                   {"user_id": session['user_id'],
                    "book_id": bookId,
                    "comment": comment,
                    "rating": rating})

        # Commit transactions to DB and close the connection
        db.commit()

        flash('Review submitted!', 'info')

        return redirect("/book/" + isbn)

    # Take the book ISBN and redirect to his page (GET)
    else:
        currentuser = session["user_id"]
        row = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn = :isbn",
                         {"isbn": isbn})

        bookInfo = row.fetchall()

        """ GOODREADS reviews """

        # Read API key from env variable
        key = os.getenv("API_KEY")

        # Query the api with key and ISBN as parameters
        query = requests.get("https://www.goodreads.com/book/review_counts.json",
                             params={"key": key, "isbns": isbn})

        # Convert the response to JSON
        response = query.json()

        # "Clean" the JSON before passing it to the bookInfo list
        response = response['books'][0]

        # Append it as the second element on the list. [1]
        bookInfo.append(response)

        """ Users reviews """

        # Search book_id by ISBN
        row = db.execute("SELECT isbn FROM books WHERE isbn = :isbn",
                         {"isbn": isbn})
        # Save id into variable
        book = row.fetchone()  # (id,)
        book = book[0]

        # Fetch book reviews
        # Date formatting (https://www.postgresql.org/docs/9.1/functions-formatting.html)
        results = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND isbn = isbn",
                          {"user_id": currentuser,
                           "isbn": book})
        reviews = results.fetchall()

        return render_template("book.html", bookInfo=bookInfo, reviews=reviews)


@app.route("/api/<isbn>", methods=['GET'])
# @login_required
def api_call(isbn):
    # COUNT returns rowcount
    # SUM returns sum selected cells' values
    # INNER JOIN associates books with reviews tables

    row = db.execute("SELECT title, author, year, isbn, \
                    COUNT(reviews.id) as review_count, \
                    AVG(reviews.rating) as average_score \
                    FROM books \
                    INNER JOIN reviews \
                    ON books.id = reviews.book_id \
                    WHERE isbn = :isbn \
                    GROUP BY title, author, year, isbn",
                     {"isbn": isbn})

    # Error checking
    if row.rowcount != 1:
        return jsonify({"Error": "Invalid book ISBN"}), 422

    # Fetch result from RowProxy
    tmp = row.fetchone()

    # Convert to dict
    result = dict(tmp.items())

    # Round Avg Score to 2 decimal. This returns a string which does not meet the requirement.
    # https://floating-point-gui.de/languages/python/
    result['average_score'] = float('%.2f' % (result['average_score']))

    return jsonify(result)


