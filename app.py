import os

from flask import Flask
from flask import render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from flask_bcrypt import Bcrypt
# upload image
from flask_uploads import UploadSet
from flask_uploads import configure_uploads
from flask_uploads import IMAGES, patch_request_class

# use this update to fix the  from werkzeug import secure_filename, FileStorage
# ImportError: cannot import name 'secure_filename'
# pip install -U Werkzeug==0.16.0
# set maximum file size, default is 16MB


# from form import FormContact,Registration,LogForm

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'hard to guess'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///website_flask.db"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# EMAIL config
app.config['MAIL_USERNAME'] = ""  # os.environ['EMAIL_USERNAME']
app.config['MAIL_PASSWORD'] = ""
app.config['MAIL_TLS'] = True
app.config['MAIL_SERVER'] = 'smtp.mail.com'
app.config['MAIL_PORT'] = 587
# Upload Configuration
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + "/static"

db = SQLAlchemy(app)
# MAIL
mail = Mail(app)
bcrypt = Bcrypt(app)

# UPLOAD Then define Upload format and file size.
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

from model import User, Role
from form import ContactForm, RegiForm, LoginForm, UploadForm


# EMAIL code
def send_mail(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to], sender=app.config['MAIL_USERNAME'])
    # msg.body= render_template(template + '.txt',**kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)


@app.before_first_request
def create_db():
    db.drop_all()
    db.create_all()
    role_admin = Role(role_name='Admin')
    role_user = Role(role_name='User')
    role_teacher = Role(role_name='Teacher')
    pass_c = bcrypt.generate_password_hash("123456")
    user_admin = User(name="Mohammad", family_name="Ghazi", username="admin", email="admin@admin.com", password=pass_c,
                      role_name=role_admin)
    db.session.add_all([role_admin, role_user, role_teacher])
    db.session.add(user_admin)
    db.session.commit()
    # user_query = User.query.filter_by(username="admin").first()
    # print(user_query.name)


@app.route('/dashboard')
def dashboard():  # put application's code here
    if session.get('username'):
        title = "Information System Flask session 2"
        pagename = "Dashboard"
        return render_template("dashboard.html", title=title, pagename=pagename)
    else:
        return redirect(url_for('login_page'))


@app.route('/contact', methods=['POST', 'GET'])
def contact_page():
    form = ContactForm()
    title = "Information System Flask session 2"
    pagename = "Contact Page"
    name = None
    if form.validate_on_submit():
        name = form.name.data
    return render_template("contact.html", name=name, form=form, title=title, pagename=pagename)


@app.route('/register', methods=['POST', 'GET'])
def register_page():
    form = RegiForm()
    if form.validate_on_submit():
        username = form.username.data
        role_name = Role.query.filter_by(role_name="User").first()
        pass_c = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name=form.name.data,
                        family_name=form.family_name.data,
                        username=form.username.data,
                        email=form.mail.data,
                        password=pass_c,
                        role_name=role_name)
        db.session.add(new_user)
        db.session.commit()
        # send_mail(form.mail.data,"New User!","mail",username=username)
        # session['username']= username
        return redirect(url_for('index'))
    return render_template('register_form.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data

        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                session['username'] = username
                session['id'] = user.id
                return redirect(url_for('dashbaord'))
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


# Create a route for Upload request
# Upload images
@app.route("/upload", methods=["POST", "GET"])
def upload():
    if not (session.get("username")) and session.get("username") == None:
        return redirect(url_for("login_page"))
    folder_name = str(session.get('username'))
    if not os.path.exists('static/' + str(folder_name)):
        os.makedirs('static/' + str(folder_name))
    file_url = os.listdir('static/' + str(folder_name))
    file_url = [str(folder_name) + "/" + file for file in file_url]
    formupload = UploadForm()
    print folder_name
    if formupload.validate_on_submit():
        filename = photos.save(formupload.file.data,
                               name=folder_name + '.jpg', folder=folder_name)
        file_url.append(filename)
    return render_template("upload.html", formupload=formupload, filelist=file_url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main_page'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/business')
def business():
    return render_template('pricing.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run()
