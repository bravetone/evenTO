from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,FileField
from wtforms.validators import DataRequired, Length,ValidationError
from app import User
#pip install email_validator




class ContactForm(FlaskForm):
    name = StringField('Name:',validators=[DataRequired(),Length(min=3,max=10,message="some thing else")])
    submit = SubmitField('Send')


class RegiForm(FlaskForm):
    name = StringField('Name:',validators=[DataRequired(),Length(min=3,max=20)])
    family_name = StringField('Surname:', validators=[DataRequired(), Length(min=3, max=20)])
    username = StringField('Username:',validators=[DataRequired(),Length(min=3,max=15)])
    mail=StringField('E-Mail',validators=[DataRequired()])
    password = PasswordField('Password:' ,validators=[DataRequired(),Length(min=3,max=24)])
    submit = SubmitField('Register')

    def validate_username(self,username):
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            raise ValidationError("User with name ' %s ' exist!" % self.username.data)


class LoginForm(FlaskForm):
    username = StringField('Username:',validators=[DataRequired(),Length(min=3,max=10)])
    password = PasswordField('Password:' ,validators=[DataRequired(),Length(min=3,max=10)])
    submit = SubmitField('Login')


#UPLOAD Class
class UploadForm(FlaskForm):
    file = FileField('file',validators=[DataRequired()])
    upload=SubmitField('upload')