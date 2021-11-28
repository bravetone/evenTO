from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired,ValidationError, Email, EqualTo, Length
from website.model import User


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
    file = FileField('file', validators=[DataRequired()])
    upload = SubmitField('upload')


