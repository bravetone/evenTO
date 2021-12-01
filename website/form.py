from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, SelectField, Form
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from website.model import User, EventOwner, Event, Choice, choice_query
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
    #username = StringField(label='Name:', validators=[DataRequired(), Length(min=2, max=30)])
    #mail = StringField(label='E-Mail', validators=[DataRequired(), Email()])
    title = StringField(label='Title:', validators=[DataRequired(), Length(min=2, max=30)])
    organizer = StringField(label='Name:', validators=[DataRequired(), Length(min=2, max=30)],
                            render_kw={'readonly': True})
    #type = StringField(label='Type:', validators=[DataRequired(), Length(min=2, max=30)])
    type = QuerySelectField(query_factory=choice_query, allow_blank=False, get_label='name')
    #type = SelectField('Type:', choices=[('Cafe', 'Cafe'), ('Club', 'Club'),
     #                                   ('Restaurants', 'Restaurants'), ('Exhibitions', 'Exhibitions')
     #                                   ])
    description = StringField(label='description',validators=[DataRequired(), Length(min=10, max=250)])
    address = StringField(label='address',validators=[DataRequired(), Length(min=10, max=50)])
    file = FileField(label='file', validators=[DataRequired()])
    price = StringField(label='Price:',validators=[DataRequired(),Length(min=2, max=10)])
    upload = SubmitField(label='Post')

   # def validate_username(self, username_to_check):
   #     if username_to_check.data != current_user.username:
   #         user = User.query.filter_by(username=username_to_check.data).first()
   #         if user:
   #             raise ValidationError("' %s ' is not your username!" % self.username.data)

   # def validate_mail(self, mail_to_check):
   #     if mail_to_check.data != current_user.mail:
   #         mail = User.query.filter_by(mail=mail_to_check.data).first()
   #         if mail:
   #             raise ValidationError('Email Address is different from your current address')


#search form
class SearchForm(FlaskForm):
    #choices = [("Type",UploadForm.type),("Location",UploadForm.location)]
    #select = SelectField('Type', choices=choices)
    searched = StringField('Searched:', validators=[DataRequired(), Length(min=3, max=10)])
    submit = SubmitField('Submit')

