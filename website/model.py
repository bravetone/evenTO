from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin, current_user
from hashlib import md5
from website import bcrypt
from website import db, login_manager
from sqlalchemy.ext.hybrid import hybrid_property


def printf(x):
    print x


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
                     )


# No need to think like user should follow eventowner kind of relation because on the
# website users will only see the event owners anyway.
# likes = db.Table('likes',
#                  db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
#                  db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
#                  )


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
    likes = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    music_id = db.Column(db.Integer, db.ForeignKey('music.id'))
    category = db.relationship(
        'Category', backref=db.backref('event', lazy='dynamic'))
    music = db.relationship('Music', backref=db.backref('event', lazy='dynamic'))

    # description = db.Column(db.String(length=1024), nullable=True)
    # date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20))

    owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, owner, title, price, address, category, music, image_file):
        self.owner = owner
        self.title = title
        self.price = price
        self.address = address
        self.category = category
        self.music = music
        self.image_file = image_file

    def __repr__(self):
        return '{}'.format(self.title)

    @hybrid_property
    def likes(self):
        return EventLike.query.filter(
            EventLike.event_id == self.id
        ).count()

    @likes.expression
    def likes(cls):
        return db.select([db.func.count(EventLike.user_id)])\
            .where(EventLike.event_id == cls.id)\
            .label('total_likes')


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
    liked = db.relationship('EventLike', foreign_keys='EventLike.user_id', backref='user', lazy='dynamic')

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

    def liked_posts(self):
        # liked = EventLike.query.filter(EventLike.user_id == self.id)
        liked = Event.query.join(EventLike, (EventLike.event_id == Event.id)).filter(EventLike.user_id == self.id)
        return liked

    def is_liked(self, event):
        return EventLike.query.filter(
            EventLike.user_id == self.id,
            EventLike.event_id == event.id
        ).count() > 0

    def like(self, event):
        if not self.is_liked(event):
            new_like = EventLike(user_id=self.id, event_id=event.id)
            db.session.add(new_like)
            return True
        else:
            return False

    def unlike(self, event):
        if self.is_liked(event):
            like = EventLike.query.filter_by(user_id=self.id, event_id=event.id)
            like.delete()
            return True
        else:
            return False

    def owned_events(self):
        return Event.query.filter(Event.owner == self.username)

    # def events_owned(self):
    #     events = Event.query.join(User).filter(event.owner == user.id)


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


class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}'.format(self.name)


class EventLike(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user = db.relationship('User', backref=db.backref('comment', lazy='dynamic'))
    event = db.relationship('Event', backref=db.backref('comment', lazy='dynamic'))

    def __init__(self, text, user, event):
        self.text = text
        self.user = user
        self.event = event


def choice_query():
    return Category.query


def music_query():
    return Music.query
