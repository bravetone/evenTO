from website import db, login_manager
from website import bcrypt
from flask_login import UserMixin


def printf(x):
    print x


@login_manager.user_loader
def load_user(user_id):
    """"Check if user is logged-in upon page load"""
    #if user_id is not None:
    return User.query.get(int(user_id))
   # return None


@login_manager.unauthorized_handler
def unauthorized():
    """"Check if user is logged-in upon page load"""
    return "You are not logged in. Click here to get <a href="+ str("/login")+">back to Login Page</a>"


class Event(db.Model):
    __tablename__ = "event"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(1024), nullable=False, unique=True)
    type = db.Column(db.String(30), nullable=False)
    images = db.relationship('Img', backref='img', lazy=True)
    owner = db.Column(db.Integer(), db.ForeignKey('users.id'))
    review = db.relationship('Review',backref='review',lazy=True)
    #events own the images, events own the review

    def __repr__(self):
        return 'Event: {}'.format(self.name)


class Img(db.Model):
    __tablename__="img"
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    event_img = db.Column(db.Integer(), db.ForeignKey('event.id'))


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), nullable=False)
    #users = db.relationship('User', backref='role_name')


class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(255), nullable=False)


class Reservation(db.Model):
    __tablename__ = 'reservation'


class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.Integer, primary_key=True)
    sub_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
    sub_type = db.Column(db.Integer, primary_key=True)

    def get_member_username(self):
        return User.query.get(self.sub_id).username


class USER:
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    family_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, index=True)
    mail = db.Column(db.String(100), unique=True, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    age = db.column(db.Integer)
    sex = db.Column(db.String(10),default='Prefer not to say')

    def __init__(self):
        return


class EventOwner(db.Model,UserMixin,USER):
    __tablename__='eventowner'
    sub_type = db.Column(db.String,nullable=False, default=00)
    events = db.relationship('Event', backref='events', lazy=True)

    def __init__(self, **kwargs):
        super(USER, self).__init__(**kwargs)
        self.set_defaultImg()
        self.set_file_address()

    def __repr__(self):
        return '<Event Owner {}>'.format(self.username)

    # eventOwner owns the events


class User(db.Model, UserMixin, USER):
    __tablename__ = "users"
    review = db.relationship('Review', backref='review', lazy=True)
    #user owns the review

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.set_defaultImg()
        self.set_file_address()

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
