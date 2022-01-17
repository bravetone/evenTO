from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, PasswordField, FileField, SelectField, Form, DecimalField, IntegerField
from wtforms.validators import DataRequired,InputRequired, ValidationError, Email, EqualTo, Length, NumberRange
from website.model import User, Event, Category, choice_query, role_query, music_query
from wtforms.ext.sqlalchemy.fields import QuerySelectField


class ContactForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired(), Length(min=3, max=10, message="some thing else")])
    submit = SubmitField('Send')


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError("User with name ' %s ' exist!" % self.username.data)

    def validate_mail(self, mail_to_check):
        mail = User.query.filter_by(mail=mail_to_check.data).first()
        if mail:
            raise ValidationError('Email Address already exists! Please try a email address!')

    name = StringField(label='Name:', validators=[DataRequired(), Length(min=2, max=20)])
    role = QuerySelectField(query_factory=role_query, allow_blank=False, label='Who are you?')
    family_name = StringField(label='Surname:', validators=[DataRequired(), Length(min=3, max=20)])
    username = StringField(label='Username:', validators=[DataRequired(), Length(min=3, max=15)])
    mail = StringField(label='E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password:', validators=[DataRequired(), Length(min=3, max=24)])
    #password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password'), ])
    submit = SubmitField(label='Register')


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired(), Length(min=3, max=10)])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=3,)])
    submit = SubmitField('Login')


# UPLOAD Class
class UploadForm(FlaskForm):
    title = StringField(label='Title:', validators=[InputRequired(), Length(min=2, max=30)])
    organizer = StringField(label='Name:', validators=[DataRequired(), Length(min=2, max=30)],
                            render_kw={'readonly': True})
    #category = SelectField('Category', validators=[InputRequired()] ,coerce=int, choices=choice_query)
    #types = [("Cafe","Cafe"), ("Restaurant","Restaurant"), ("Club","Club")]
    #event_type= RadioField("Type", choices=types)
    category = QuerySelectField(query_factory=choice_query, allow_blank=False, label='Category')
    music_type = QuerySelectField(query_factory=music_query, allow_blank=False, label='Music')

    #description = StringField(label='description',validators=[DataRequired(), Length(min=1, max=250)])
    address = StringField(label='Address',validators=[InputRequired(), Length(min=1, max=50)])
    image = FileField(label='Image')
    price = DecimalField(label='Price:', validators=[InputRequired(), NumberRange(min=1, max=100)])
    upload = SubmitField(label='Post')


class CategoryField(SelectField):

    def iter_choices(self): #we overwrite this to get values of categories from the database but it can be done with Queryselectfield too
        categories = [(c.id, c.name) for c in Category.query.all()]
        for value, label in categories:
            yield value, label, self.coerce(value) == self.data

    def pre_validate(self, form):
        for v, _ in [(c.id, c.name) for c in Category.query.all()]:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))


#search form
class SearchForm(FlaskForm):
    #choices = [("Type",UploadForm.type),("Location",UploadForm.location)]
    #select = SelectField('Type', choices=choices)
    searched = StringField(label='Searched:')
    category = QuerySelectField(query_factory=choice_query, allow_blank=False, label='Category')
    submit = SubmitField('Submit')


def check_duplicate_category(case_sensitive=True):
    def _check_duplicate(form, field):
        if case_sensitive:
            res = Category.query.filter(
                Category.name.like('%' + field.data + '%') ).first()
        else:
            res = Category.query.filter(
                Category.name.ilike('%' + field.data + '%') ).first()
        if res:
            raise ValidationError(
                                  'Category named %s already exists' % field.data
            )
    return _check_duplicate


class CategoryForm(FlaskForm):
    name = StringField('Name',validators=[InputRequired(),check_duplicate_category()])


class EditProfileForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user and current_user != user:
            raise ValidationError("User with name ' %s ' exist!" % self.username.data)

    def validate_mail(self, mail_to_check):
        mail = User.query.filter_by(mail=mail_to_check.data).first()
        if mail and current_user != mail:
            raise ValidationError('Email Address already exists! Please try a email address!')

    name = StringField(label='Name', validators=[DataRequired(), Length(min=2, max=20)])
    family_name = StringField(label='Surname', validators=[DataRequired(), Length(min=3, max=20)])
    username = StringField(label='Username', validators=[DataRequired(), Length(min=3, max=15)])
    mail = StringField(label='E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField(label='New Password')
    #password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password'), ])
    submit = SubmitField(label='Submit')