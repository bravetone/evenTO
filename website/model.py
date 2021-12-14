from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin, current_user
from hashlib import md5
from website import bcrypt
from website import db, login_manager


def printf(x):
    print x


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
                     )
# No need to think like user should follow eventowner kind of relation because on the
# website users will only see the event owners anyway.


@login_manager.unauthorized_handler
def unauthorized():
    """"Check if user is logged-in upon page load"""
    return "You are not logged in. Click here to get <a href=" + str("/login") + ">back to Login Page</a>"


class Event(db.Model):
    __tablename__ = "event"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(length=1024), nullable=False)
    price = db.Column(db.Float)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    address = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship(
        'Category', backref=db.backref('event', lazy='dynamic'))

    # description = db.Column(db.String(length=1024), nullable=True)
    # date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20))

    owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, owner, title, price, address, category, image_file):
        self.owner = owner
        self.title = title
        self.price = price
        self.address = address
        self.category = category
        self.image_file = image_file

    def __repr__(self):
        return '{}'.format(self.title)


# eventOwner owns the events
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    family_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, index=True)
    mail = db.Column(db.String(100), unique=True, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship(
        'Role', backref=db.backref('users', lazy='dynamic'))
    event = db.relationship('Event', backref='event_owner', lazy=True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(user_id)
        except:
            return None

    def avatar(self, size):
        digest = md5(self.mail.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

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
        followed = Event.query.join(
            followers, (followers.c.followed_id == Event.owner)).filter(followers.c.follower_id == self.id)
        own = Event.query.filter_by(owner=self.id)
        return followed.union(own).order_by(Event.date_posted.desc())


def role_query():
    return Role.query


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), nullable=False)

    def __init__(self, role_name):
        self.role_name = role_name

    def __repr__(self):
        return '{}'.format(self.role_name)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}'.format(self.name)


def choice_query():
    return Category.query


