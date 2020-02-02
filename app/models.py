from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from app import db


""" Book """
class Book:
    
    def __init__(self, isbn, title, author, year):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year

    def __repr__(self):
        return '<Book {}>'.format(self.body)

""" Review """
class Review:

    def __init__(self, book, user, body, rating):
        self.book = book
        self.user = user
        self.body = body
        self.rating = rating

    def __repr__(self):
        return '<Review {}>'.format(self.body)

""" User """
class User():

    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return '<User {}>'.format(self.username)

    # Password management
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Profile management
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)


"""
    Old models before i read the requirement below. 
    - You should be using raw SQL commands (as via SQLAlchemy’s execute method) in order to make database queries. 
    You should not use the SQLAlchemy ORM (if familiar with it) for this project.


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13))
    title = db.Column(db.String(140))
    author = db.Column(db.String(140))
    year = db.Column(db.String(4))
    reviews = db.relationship('Review', backref='book', lazy='dynamic')
    
    def __repr__(self):
        return '<Book {}>'.format(self.body)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    rating = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Review {}>'.format(self.body)

    def goodreads_book_info(self, isbn):
        r = request.get('https://www.goodreads.com/book/review_counts.json?isbns={book_isbn}', book)
        #https://www.goodreads.com/book/review_counts.json?isbns=0441172717
        #https://www.goodreads.com/search.xml?key=udQ1yheDkLrnyrKcXXlw&q=Ender%27s+Game



followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    # Relations
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        #include own posts
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
"""