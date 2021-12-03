from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin

from website import bcrypt
from website import db, login_manager


def printf(x):
    print x


# return None
@login_manager.unauthorized_handler
def unauthorized():
    """"Check if user is logged-in upon page load"""
    return "You are not logged in. Click here to get <a href=" + str("/login") + ">back to Login Page</a>"


class Reservation(db.Model):  # users reserve events [many-to-many relationships]
    __tablename__ = 'reservations'
    id = db.Column(db.Integer,  # need to figure out how QR code can be stored
                   primary_key=True,
                   index=True)
    reserver_id = db.Column('Users', db.Integer, db.ForeignKey('users.id'))
    reserved_id = db.Column('Event', db.Integer, db.ForeignKey('event.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Follow(db.Model):  # users following events [many-to-many relationships]
    __tablename__ = 'follows'
    id = db.Column(db.Integer,
                   primary_key=True,
                   index=True)
    follower_id = db.Column('Users', db.Integer, db.ForeignKey('users.id'))
    followed_id = db.Column('EventOwner', db.Integer, db.ForeignKey('eventowners.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    __tablename__ = "event"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(1024), nullable=True, unique=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.Integer(), db.ForeignKey('category.id'), nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    owner = db.Column(db.Integer(), db.ForeignKey('eventowners.username'), nullable=False)
    reserver = db.relationship('Reservation', foreign_keys=[Reservation.reserved_id],
                               backref=db.backref('reserved', lazy='joined'), lazy='dynamic',
                               cascade='all, delete-orphan')

    # review = db.relationship('Review',backref='review',lazy=True)
    # events own the images, events own the review

    def __repr__(self):
        return 'Event: {}'.format(self.name)

# class Img(db.Model):
#    __tablename__="img"
#    id = db.Column(db.Integer, primary_key=True)
#    img = db.Column(db.Text, unique=True, nullable=False)
#    name = db.Column(db.String(100), nullable=False)
#    mimetype = db.Column(db.Text, nullable=False)
#    event_img = db.Column(db.Integer(), db.ForeignKey('event.id'),nullable=True)


class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(255), nullable=False)


class USER:
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    family_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, index=True)
    mail = db.Column(db.String(100), unique=True, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    age = db.Column(db.Integer, nullable=True)
    sex = db.Column(db.String(10), default='Prefer not to say')


class EventOwner(db.Model, UserMixin, USER):
    __tablename__ = 'eventowners'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    sub_type = db.Column(db.String, nullable=True, default=00)
    events = db.relationship('Event', backref='eventowner', lazy=True)
    follower = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'), lazy='dynamic',
                               cascade='all, delete-orphan')

    @property
    def followed_posts(self):  # displaying the events that users want to see by following the eventowners
        return Event.query.join(Follow, Follow.followed_id == Event.owner) \
            .filter(Follow.follower_id == self.id)

    def follow(self, eventt):
        if not self.is_following(eventt):
            f = Follow(follower=self, followed=eventt)
            db.session.add(f)

    def unfollow(self, eventt):
        f = self.followed.filter_by(followed_id=eventt.id).first()
        if f:
            db.session.delete(f)

    def is_followed_by(self, eventt):
        return self.followers.filter_by(follower_id=eventt.id).first() is not None

    def is_following(self, eventt):
        return self.followed.filter_by(
            followed_id=eventt.id).first() is not None

    def __init__(self, **kwargs):
        super(EventOwner, self).__init__(**kwargs)
        return

    def __repr__(self):
        return '<Event Owner {}>'.format(self.username)


# eventOwner owns the events

class User(db.Model, UserMixin, USER):
    __tablename__ = "users"
    # review = db.relationship('Review', backref='revieww', lazy=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'), lazy='dynamic',
                               cascade='all, delete-orphan')
    reserved = db.relationship('Reservation', foreign_keys=[Reservation.reserver_id],
                               backref=db.backref('reserver', lazy='joined'), lazy='dynamic',
                               cascade='all, delete-orphan')

    # user owns the review
    def __repr__(self):
        return '<User {}>'.format(self.username)

    @property
    def password(self):
        return self.password

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(user_id)
        except:
            return None

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.mail == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(name=forgery_py.name.first_name(),
                     family_name=forgery_py.name.last_name(),
                     username=forgery_py.internet.user_name(True),
                     mail=forgery_py.internet.email_address(),
                     password=forgery_py.lorem_ipsum.word(),
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return 'Role {}'.format(self.role_name)

    @staticmethod
    def insert_role():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT, True),
            'EventOwner': (Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False),
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permissions = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
        db.session.commit()


class Choice(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    event = db.relationship('Event', backref='events', lazy=True)

    def __repr__(self):
        return '[Choice {}]'.format(self.name)


def choice_query():
    return Choice.query


class Permission:
    FOLLOW = 0X01  # follow other users
    COMMENT = 0X02  # comment on articles written by others
    WRITE_ARTICLES = 0X04  # write original articles
    MODERATE_COMMENTS = 0X08  # suppress offensive comments made by others
    ADMINISTER = 0X80  # administravite access to the site
