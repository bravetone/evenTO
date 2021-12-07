from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin, current_user

from website import bcrypt
from website import db, login_manager


def printf(x):
    print x


# return None
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

    # owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, title, price, address, category, image_file):
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
    name = db.Column(db.String(length=1024), nullable=False)
    family_name = db.Column(db.String(length=1024), nullable=False)
    username = db.Column(db.String(length=1024), unique=True, index=True)
    mail = db.Column(db.String(length=1024), unique=True, index=True)
    password_hash = db.Column(db.String(length=1024), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship(
        'Role', backref=db.backref('users', lazy='dynamic'))

    # events = db.relationship('Event', backref='eventowner', lazy=True)
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.role_id == 0:
                self.Role = Role.query.filter_by(name='User').first()

            else:
                self.Role = Role.query.filter_by(name='Event Owner').first()

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




def role_query():
    return Role.query


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), nullable=False)
    permissions = db.Column(db.Integer)

    def __init__(self, role_name):
        self.role_name = role_name

    def __repr__(self):
        return '{}'.format(self.role_name)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.COMMENT],
            'Event Owner': [Permission.WRITE],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}'.format(self.name)


def choice_query():
    return Category.query
