import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bootstrap import Bootstrap
import requests
import json



app = Flask(__name__)
engine = create_engine("postgres://bjwxmuebywiexo:cbb7614809a4bba5aa0a32b18dbef509fed6732c10ca07a2b81dc2dac043d721@ec2-54-211-210-149.compute-1.amazonaws.com:5432/d2n3ohvdkibnt3")
db = scoped_session(sessionmaker(bind=engine))
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
#api = Api(app)
bootstrap = Bootstrap(app)
GRRequestKey = "GZ4LbC681pT1BZJO6WLQ"


@app.route("/")
def index():
    if session.get("USERNAME") is None:
        return render_template("signin.html")
    if not session.get("USERNAME") is None:
        username = session.get("USERNAME")
    if username == "":
        return render_template("signin.html")
    if username:
        return redirect(url_for("profile"))



@app.route("/book/<int:book_id>")
def book(book_id):
#    """Lists details about a single book."""

    session["book_id"] = book_id
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    preconfiguredISBN = book.isbn
    if len(preconfiguredISBN) == 5:
        isbnG = "00000" + preconfiguredISBN;
    if len(preconfiguredISBN) == 6:
        isbnG = "0000" + preconfiguredISBN;
    if len(preconfiguredISBN) == 7:
        isbnG = "000" + preconfiguredISBN;
    if len(preconfiguredISBN) == 8:
        isbnG = "00" + preconfiguredISBN;
    if len(preconfiguredISBN) == 9:
        isbnG = "0" + preconfiguredISBN;
    if  len(preconfiguredISBN) == 10:
        isbnG = preconfiguredISBN
    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GRRequestKey, "isbns": isbnG})
    contentJson = response.json()

    listOfReviews = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book_id}).fetchall()
    if listOfReviews:
        existingReviews = listOfReviews
    if not listOfReviews:
        existingReviews = ""

    return render_template("book.html", book=book, content=contentJson, reviews=existingReviews)

    #reviewCount=reviewCount, averageRating=averageRating
    #content = (json.loads(contentJson))
    #reviewCount = content.books[0].reviews_count
    #averageRating = content.books[0].average_rating

@app.route("/postreview", methods=["GET", "POST"])
def postreview():
    session["ERROR"] =""
    req = request.form
    textofreview = req.get("textofreview")
    book_id = session.get("book_id")
    username = session.get("USERNAME")
    starsStr = req.get("ratings")
    ratings = int(starsStr)
    stars = ratings

    user = db.execute("SELECT * FROM users WHERE name = '%s'" % (username)).fetchone()
    reviewDone = db.execute("SELECT * FROM reviews WHERE user_id = %d" % (user.id)).fetchall()
    whetherReviewDone = False
    if reviewDone:
        for review in reviewDone:
            if review.book_id == book_id:
                whetherReviewDone = True
    if  whetherReviewDone is False:
        commandReview = "INSERT INTO reviews (textofreview, rating, book_id, user_id, stars) VALUES ('%s', '%d', '%d', '%d', '%d')" % (textofreview, ratings, book_id, user.id, stars)
        db.execute(commandReview)
        db.commit()
        errorMessage = "Review Done"
        session["ERROR"] = errorMessage
        #return redirect("/book/" + str(book_id)
        return redirect(url_for("book", book_id=book_id))
    if whetherReviewDone is True:
        errorMessage = "You have already reviewed this book"
        session["ERROR"] = errorMessage
        return redirect(url_for("book", book_id=book_id))


@app.route("/searchforbook")
def searchforbook():
    return render_template("searchforbook.html")

@app.route("/searchforbookbytitle", methods=["GET", "POST"])
def searchforbookbytitle():
    session.pop("book_id", None)
    if session.get("USERNAME") is None:
        return render_template("signin.html")
    if request.method == "POST":
            req = request.form
            gettitle = req.get("booktitle")
            if gettitle:
                findBookCommand = "SELECT * FROM books WHERE title LIKE" + " '%" + gettitle + "%'"
            if not gettitle:
                findBookCommand = "SELECT * FROM books"
            if findBookCommand:
                findBook = db.execute(findBookCommand).fetchall()
                if findBook == []:
                    session["NOTFOUND"] = "Books not found"
                if not findBook == []:
                    session["NOTFOUND"] = ""
                return render_template("books.html", books=findBook)
    return render_template("searchforbook.html")

@app.route("/searchforbookbyauthor", methods=["GET", "POST"])
def searchforbookbyauthor():
    session.pop("book_id", None)
    if session.get("USERNAME") is None:
        return render_template("signin.html")
    if request.method == "POST":
            req = request.form
            getauthor = req.get("authorname")

            if getauthor:
                findBookCommand = "SELECT * FROM books WHERE author LIKE" + " '%" + getauthor + "%'"
            if not getauthor:
                findBookCommand = "SELECT * FROM books"
            if findBookCommand:
                findBook = db.execute(findBookCommand).fetchall()
                if findBook == []:
                    session["NOTFOUND"] = "Books not found"
                if not findBook == []:
                    session["NOTFOUND"] = ""
                return render_template("books.html", books=findBook)
    return render_template("searchforbook.html")

@app.route("/searchforbookbyisbn", methods=["GET", "POST"])
def searchforbookbyisbn():
    session.pop("book_id", None)
    if session.get("USERNAME") is None:
        return render_template("signin.html")
    if request.method == "POST":
            req = request.form
            getISBN = req.get("isbn")
            if getISBN:
                findBookCommand = "SELECT * FROM books WHERE isbn LIKE" + " '%" + getISBN + "%'"
            if not getISBN:
                findBookCommand = "SELECT * FROM books"
            if findBookCommand:
                findBook = db.execute(findBookCommand).fetchall()
                if findBook == []:
                    session["NOTFOUND"] = "Books not found"
                if not findBook == []:
                    session["NOTFOUND"] = ""
                return render_template("books.html", books=findBook)
    return render_template("searchforbook.html")

@app.route("/searchforbookbyyear", methods=["GET", "POST"])
def searchforbookbyyear():
    session.pop("book_id", None)
    if session.get("USERNAME") is None:
        return render_template("signin.html")
    if request.method == "POST":
            req = request.form
            getYear = req.get("year")
            if getYear:
                findBookCommand = "SELECT * FROM books WHERE year::text LIKE" + " '%" + getYear + "%'"
            if not getYear:
                findBookCommand = "SELECT * FROM books"
            if findBookCommand:
                findBook = db.execute(findBookCommand).fetchall()
                if findBook == []:
                    session["NOTFOUND"] = "Books not found"
                if not findBook == []:
                    session["NOTFOUND"] = ""
                return render_template("books.html", books=findBook)
    return render_template("searchforbook.html")















@app.route("/signout")
def signout():
    if not session.get("USERNAME") is None:
        username = session.get("USERNAME")
        db.execute("UPDATE users SET isLOGIN = '0' WHERE name = '%s'" % (username))
        db.commit()
        session.pop("LOGIN", None)
        session.pop("USERNAME", None)
        session.pop("book_id", None)
        session.pop("NOTFOUND", None)
        return render_template("signout.html")
    if session.get("USERNAME") is None:
        session.pop("LOGIN", None)
        session.pop("book_id", None)
        return render_template("signout.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
            req = request.form
            getpassword = req.get("password")
            getusername = req.get("username")
        #remember to make sure sign up cannot have same user Name
            userDetails = db.execute("SELECT * FROM users WHERE name = '%s'" % (getusername)).fetchone()
            if userDetails:
                submittedusername = userDetails[1]
                submittedpassword = userDetails[2]
            if not userDetails:
                submittedusername = None
                submittedpassword = None
            if  not submittedusername:
                return render_template("signin.html", errorMessage="Password or User Name is Wrong / Does Not Exist")
            if (submittedusername) and (not submittedpassword):
                return render_template("signin.html", errorMessage="Password or User Name is Wrong / Does Not Exist")
            if (submittedusername == getusername) and (getpassword != submittedpassword):
                return render_template("signin.html", errorMessage="Password or User Name is Wrong / Does Not Exist")
            if (submittedusername == getusername) and (getpassword == submittedpassword):
                session["USERNAME"] = submittedusername
                session["LOGIN"] = "True"
                db.execute("UPDATE users SET isLOGIN = '1' WHERE name = '%s'" % (submittedusername))
                db.commit()
                return redirect(url_for("profile"))
    return render_template("signin.html")

@app.route("/newUser", methods=["GET", "POST"])
def newUser():
    if request.method == "POST":
            req = request.form
            getpassword = req.get("password")
            getusername = req.get("username")
        #remember to make sure sign up cannot have same user Name
            userDetails = db.execute("SELECT * FROM users WHERE name = '%s'" % (getusername)).fetchone()
            if userDetails:
                submittedusername = userDetails[1]
                submittedpassword = userDetails[2]
                return render_template("newUser.html", errorMessage="Username already exist. Choose another one")
            if not userDetails:
                submittedusername = getusername
                submittedpassword = getpassword
                command = "INSERT INTO users (name, password, islogin) VALUES ('%s', '%s', '%s')" % (submittedusername, submittedpassword,'1')
                db.execute(command)
                db.commit()
                session["USERNAME"] = getusername
                session["LOGIN"] = "True"
                return redirect(url_for("profile"))
    return render_template("newUser.html")



@app.route("/profile")
def profile():

    booksReviewed = { }
    if not session.get("USERNAME") is None:
        username = session.get("USERNAME")
        userDetails = db.execute("SELECT * FROM users WHERE name = '%s'" % (username)).fetchone()
        userID = userDetails.id
        listOfReviews = db.execute("SELECT * FROM reviews WHERE user_id = %d" % (userID)).fetchall()
        if listOfReviews:
            existingReviews = listOfReviews
            for review in existingReviews:
                searchforbookidstr = review.book_id
                searchforbookid = int(searchforbookidstr)
                bookReviewed = db.execute("SELECT * FROM books WHERE id = %d" % (searchforbookid)).fetchone()
                booktitle = bookReviewed.title
                myreview = review.textofreview
                booksReviewed[booktitle] = myreview
        return render_template("profile.html", user= username, books=booksReviewed)
        if not listOfReviews:
            return render_template("profile.html", user=username, books=booksReviewed)
    if session.get("USERNAME") is None:
        return render_template("newUser.html")
    else:
        print("No username found in session")
        return redirect(url_for("abc"))


#API SECTION


@app.route('/api/<isbn>', methods=['GET'])
def get_book(isbn):
    findBookCommand = "SELECT * FROM books WHERE isbn LIKE" + " '%" + isbn + "%'"
    if findBookCommand:
        findBook = db.execute(findBookCommand).fetchone()
        if not findBook:
            return "404 ERROR!! Sorry your search is invalid!"
        if findBook:
            title = findBook.title
            author = findBook.author
            year = findBook.year
            isbn = findBook.isbn
            bookid = findBook.id
            listOfReviews = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": bookid}).fetchall()
            numberOfReviews = 0
            totalRatings = 0
            for review in listOfReviews:
                numberOfReviews = numberOfReviews + 1
                totalRatings = totalRatings + review.rating
            if not totalRatings == 0:
                averageScore = totalRatings / numberOfReviews
            if totalRatings == 0:
                averageScore = 0;

        book = {
        "title": title,
        "author": author,
        "year": year,
        "isbn": isbn,
        "review_count": numberOfReviews,
        "average_score": averageScore
        }
    return jsonify(book)
