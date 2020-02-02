from datetime import datetime
from flask import request, render_template, flash, redirect, url_for, session, jsonify
from flask_session import Session
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from app.models import User
from app.helpers import login_required
from app.forms import LoginForm, RegistrationForm, ReviewForm

import requests
import os

""" 
Routes 
"""
# Index 
@app.route("/")
@login_required
def index():
     return render_template('index.html', title='Index')

# Login screen
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        query = db.execute("SELECT * FROM users WHERE username = :username", {"username": form.username.data}).fetchone()
        # when username unknown
        if query is None:
            flash('Invalid username')
            return redirect(url_for('login'))
        user = User(query.id, query.username, query.email, query.password_hash)
        # when password incorrect
        if not user.check_password(form.password.data):
            flash('Invalid password')
            return redirect(url_for('login'))
        # start user session
        session["user_id"] = query[0]
        session["user_name"] = query[1]
        next_page = request.args.get('next')
        # login succes enter site
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        flash('Successfully logged in')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

# Lougout user
@app.route("/logout")
def logout():
    session.clear()
    flash('Successfully logged out')
    return redirect(url_for('index'))
        
# Register screen
"""Register user."""
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_check = db.execute("SELECT * FROM users WHERE username = :username", {"username": form.username.data}).fetchone()
        # check on duplicate username
        if user_check:
            flash('User already exists')
            return redirect(url_for('register'))
        email_check = db.execute("SELECT * FROM users WHERE email = :email", {"email": form.email.data}).fetchone()
        # check on duplicate email
        if email_check:
            flash('Email already exists')
            return redirect(url_for('register'))
        # create user
        username = form.username.data
        email = form.email.data
        password_hash = generate_password_hash(form.password.data)
        db.execute("INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password_hash)",{"username": username, "email": email, "password_hash":password_hash})
        db.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

# Search books
@app.route("/search")
def search():
    if request.args.get("book"):
        # search action
        search = "%" + request.args.get("book") + "%"
        books = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(:search) \
            OR LOWER(isbn) LIKE LOWER(:search) OR \
            LOWER(author) LIKE LOWER(:search) LIMIT 20", {"search" : search}).fetchall()
        if books is None:
            flash("No matches found")
            return redirect("/")
        return render_template('index.html', books=books)
    return render_template('index.html')

@app.route("/user/<username>")
@login_required
def user(username):
    user = db.execute("SELECT * FROM users WHERE username = :username", {"username" : username}).fetchone()
    return render_template("user.html", user=user)

@app.route('/books/<bookisbn>', methods=['GET', 'POST'])
@login_required
def book(bookisbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :bookisbn", {"bookisbn" : bookisbn}).fetchone()
    if book is None:
        flash("Book not found")
        return redirect(url_for("index"))  

    book_reviews = db.execute("SELECT users.username, body, rating FROM users INNER JOIN reviews on users.id = reviews.user_id WHERE book_isbn = :bookisbn", {"bookisbn": bookisbn}).fetchall()
    
    # Goodreads API call
    goodreads_call = "https://www.goodreads.com/book/review_counts.json?isbns=%2c{}&key={}".format(bookisbn, os.getenv('GOODREADS_KEY'))
    goodreads_info =  requests.get(goodreads_call).json()
    
    # when review is submitted
    form = ReviewForm()
    if form.validate_on_submit():
        review_check = db.execute("SELECT * FROM reviews WHERE user_id = :id", {"id" : session["user_id"]}).fetchone()
        if review_check is not None:
            flash('Review already submitted')
            return redirect(url_for('index'))
        review = db.execute("INSERT INTO reviews (user_id, book_isbn, body, rating ) VALUES \
            (:user_id, :book_isbn, :body, :rating)", 
            {"user_id" : session["user_id"], 
            "book_isbn" : book.isbn, 
            "body" : form.body.data, 
            "rating" : form.rating.data})
        db.commit()
        flash('Your review of the book {} is now live!'.format(book.title))
        return redirect(url_for('index'))
    return render_template('book.html', form=form, book=book, book_reviews=book_reviews, goodreads_info=goodreads_info)

@app.route('/api/<isbn>')
def api_isbn(isbn):
    book = db.execute("SELECT title, author, year, isbn  FROM books WHERE isbn = :isbn", {"isbn" : isbn}).fetchone()
    
    # non existent isbn return 404
    if book is None:
        return jsonify({"Error": "Unknown ISBN number"}), 404
    
    # turn result into dictionary
    book = dict(book)

    # 2 calculation queries to add to api call
    review_count = dict(db.execute("SELECT COUNT(*) FROM reviews WHERE book_isbn = :isbn", {"isbn" : isbn}).fetchone())
    average_score = dict(db.execute("SELECT to_char(AVG(rating), '9D99') as average_score FROM reviews WHERE book_isbn = :isbn", {"isbn" : isbn}).fetchone())
    book['average_score'] = average_score["average_score"]
    book['review_count'] = review_count["count"]
    
    # return ok
    return jsonify(book), 200