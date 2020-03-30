# Book Search App using Flask

[**Demo of live application**](http://book-search-app-anuradha.herokuapp.com/s) 


This project is based on the assignment of 
[CS50 Web Development with python and javascript](https://www.edx.org/course/cs50s-web-programming-with-python-and-javascript)



## Usage

* **Registration, Login and Logout** 
* **Import** This is the most interesting part of the project. Provided was a file called `books.csv`,
 which had a spreadsheet in CSV format of 5000 different books. Each one has an ISBN number, a title, an author, 
 and a publication year. In a Python file called  `import.py` separate from the web application, I had to write 
 a script that will take the books and import them into your PostgreSQL database. I first had to need 
 to decide what table(s) to create, what columns those tables should have, and how they should relate to one another
* **Search**  User is able to search books from the database. From the same database from which, data is fed using `books.csv`
and `import.py`
*  **Book Details** Once the user goes to book page after searching and selecting a book, user can view detailed data
of that book, which is fetched from GoodReads API.
*  **User reviews**  User can view and give review to the book on book page, which then will be saved in PostgreSQL database.


##  Setup

```bash

# Create a virtualenv (Optional but reccomended)
$ python3 -m venv myvirtualenv

# Activate the virtualenv
$ source myvirtualenv/bin/activate (Linux)

# Install all dependencies
$ pip3 install -r requirements.txt

# ENV Variables
$ export FLASK_APP = application.py # flask run
$ export DATABASE_URL = Heroku Postgres DB URI
$ export GOODREADS_KEY = Goodreads API Key. # More info: https://www.goodreads.com/api
```

##  Tech Stack

-  **Flask**  Flask is a micro web framework written in Python. It is classified as a microframework
 because it does not require particular tools or libraries. It has no database abstraction layer, 
 form validation, or any other components where pre-existing third-party libraries provide common functions. <br>
 It is used in this project to handle all the HTTP routes, rendering views and performing database queries. 
 
-  **PosgreSQL**  PostgreSQL, often simply Postgres, is an open source object-relational database management system with an 
emphasis on extensibility and standards compliance. It can handle workloads ranging from small single-machine 
applications to large Internet-facing applications with many concurrent users. <br>
 Used for storing data of the users. <br>
 Online hosted by in [Heroku](https://www.heroku.com/postgres), accessed via [Adminer](https://adminer.cs50.net/).
 
 - **Bootstrap**  Bootstrap is a free and open-source front-end Web framework. It contains HTML and CSS-based design templates 
 for typography, forms, buttons, navigation and other interface components
 as well as optional JavaScript extensions.  <br>
  Used for stylising frontend. [Get Bootstrap](https://getbootstrap.com/)
 
 
 
 
