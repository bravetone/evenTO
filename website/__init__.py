import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_moment import Moment






# upload image
from flask_uploads import UploadSet
from flask_uploads import configure_uploads
from flask_uploads import IMAGES, patch_request_class
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename, FileStorage


app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'potato'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///evenTO.db"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# EMAIL config
app.config['MAIL_USERNAME'] = "os.environ['EMAIL_USERNAME']"
app.config['MAIL_PASSWORD'] = "os.environ['EMAIL_PASSWORD']"
app.config['MAIL_TLS'] = True
app.config['MAIL_SERVER'] = 'smtp.mail.com'
app.config['MAIL_PORT'] = 587
# Upload Configuration
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + "/static"
app.config['FLASKY_POSTS_PER_PAGE'] = 10
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
#Admin
app.config['EVENTO_ADMIN']=os.environ.get('EVENTO_ADMIN')
app.config['EVENTO_MAIL_SUBJECT_PREFIX'] = '[evenTO]'
app.config['EVENTO_MAIL_SENDER'] =  'evenTO Admin <admin@evento.com>'



db = SQLAlchemy(app)
# MAIL
mail = Mail(app)
bcrypt = Bcrypt(app)
moment = Moment(app)


login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"
login_manager.init_app(app)

# UPLOAD Then define Upload format and file size.
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


from website import routes



