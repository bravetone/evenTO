import os
from website import app
from flask import render_template, flash, redirect, url_for, session
from website.model import User, Events, Role
from website.form import *
from website import db
from flask_login import login_user, logout_user, login_required


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        role_name = Role.query.filter_by(role_name="User").first()
        password_hash = form.password.data
        new_user = User(name=form.name.data,
                        family_name=form.family_name.data,
                        username=form.username.data,
                        email=form.mail.data,
                        password=password_hash,
                        role_name=role_name)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Account created successfully! You are now logged in as {}'.format(new_user.username),category='success')
        flash('Registered successfully.')
        return redirect(url_for('login_page'))
    if form.errors != {}:  #if there are no errors from the validations
        for err_msg in form.errors.values():
            flash('There was an error with creating a user: {}'.format(err_msg),category='danger')
    return render_template('register_form.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash('Logged in successfully as {}'.format(attempted_user.username), "success")
            return redirect(url_for('index'))
        else:
            flash('Username or Password Incorrect', "danger")

    return render_template('login.html', form=form)


@app.route("/logout")
def logout_page():
    
    """User log-out logic."""
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('index'))
# Create a route for Upload request
# Upload images


'''@app.route("/upload", methods=["POST", "GET"])
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
    return render_template("post_event.html", formupload=formupload, filelist=file_url) '''


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/business')
def business():
    return render_template('pricing.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/event')
def events():
    event = Events.query.all()
    return render_template('event.html',event=event)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/post')
@login_required
def post_events():

    return render_template('post_event.html')









