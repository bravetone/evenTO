import os

from flask import render_template, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required,current_user

from website import app, photos
from website import db
from website.model import User, Event, Choice, EventOwner
from website.form import RegisterForm, SearchForm, UploadForm,LoginForm


#@app.before_first_request
#def create_db():
  #  db.drop_all()
 #   db.create_all()


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    events = Event.query.order_by(Event.date_posted)
    if form.validate_on_submit():
        # Get data from submitted form
        event.searched = form.searched.data
        # Query the Database
        events = events.filter(Event.title.like('%' + event.searched + '%'))
        posts = events.order_by(Event.title).all()

        return render_template("search.html",
                               form=form,
                               searched=event.searched,
                               events=events)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data

        password_hash = form.password.data
        new_user = User(name=form.name.data,
                        family_name=form.family_name.data,
                        username=form.username.data,
                        mail=form.mail.data,
                        password=password_hash,
                        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Account created successfully! You are now logged in as {}'.format(new_user.username), category='success')
        return redirect(url_for('index'))
    if form.errors != {}:  # if there are no errors from the validations
        for err_msg in form.errors.values():
            flash('There was an error with creating a user: {}'.format(err_msg), category='danger')
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


@app.route('/', methods=['GET', 'POST'])
def index():
    formupload = UploadForm()

    return render_template('index.html',formupload=formupload)


@app.route('/business')
def business():
    return render_template('pricing.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/event')
def events():
    events = Event.query.order_by(Event.date_posted)
    return render_template('event.html', events=events)


@app.route('/event/<int:id>')
def event(id):
    event = Event.query.get_or_404(id)
    return render_template('event.html', event=event)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    event = Event.query.get_or_404(id)
    form = UploadForm()
    if form.validate_on_submit():
        event.title = form.title.data
        # post.author = form.author.data
        event.content = form.type.data
        event.content = form.location.data
        # Update Database
        db.session.add(event)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('event', id=event.id))

    if current_user.id == event.poster_id:
        event.title = form.title.data
        # post.author = form.author.data
        event.type = form.type.data
        event.location = form.location.data
        return render_template('edit_event.html', form=form)
    else:
        flash("You Aren't Authorized To Edit This Post...")
        posts = Event.query.order_by(Event.date_posted)
        return render_template("events.html", posts=posts)


@app.route('/post', methods=['GET', 'POST'])  # POST EVENT
@login_required
def post_events():
    if not os.path.exists('static/' + str(session.get('id'))):
        os.makedirs('static/' + str(session.get('id')))
    file_url = os.listdir('static/' + str(session.get('id')))
    file_url = [str(session.get('id')) + "/" +
                file for file in file_url]
    formupload = UploadForm()
    form = LoginForm()
    print session.get('email')
    eventowner = current_user.username
    formupload.organizer.data = eventowner

    if formupload.validate_on_submit():
        event = Event(title=formupload.title.data,
                      type=formupload.type.data,
                      owner=formupload.organizer.data,
                      description=formupload.description.data,
                      price=formupload.price.data,
                      location=formupload.address.data,
                      image_file=photos.save(formupload.file.data, name=str(session.get('id')) + '.jpg',
                                             folder=str(session.get('id')))
                      )
        # Clear The Form
        formupload.title.data = ''
        formupload.address.data = ''
        formupload.type.data = ''

        # file_url.append(filename)
        db.session.add(event)
        # db.session.add(filename)
        db.session.commit()
        flash('Event Posted!')
        return redirect(url_for('events'))
    return render_template('post_event.html', formupload=formupload, file_url=file_url, form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
