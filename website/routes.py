import os

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from website import app, ALLOWED_EXTENSIONS
from website import db
from website.form import RegisterForm, SearchForm, UploadForm, LoginForm, CategoryForm
from website.model import User, Event, Category, Role


# @app.before_first_request
# def create_db():
#    db.drop_all()
#    db.create_all()
#    role_user = Role(role_name="User")
#    role_owner = Role(role_name="Event Owner")
#    category_1 = Category(name="Club")
#    category_2 = Category(name="Restaurant")
#    category_3 = Category(name="Cafe")
#    db.session.add_all([category_1,category_2,category_3])
#    db.session.add_all([role_user,role_owner])
#    db.session.commit()


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


# AUTHORIZATION
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(role=Role.query.get_or_404(
            form.role.data.id),
            name=form.name.data,
            family_name=form.family_name.data,
            username=form.username.data,
            mail=form.mail.data,
            password_hash=form.password.data,
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


# MAIN PAGES
@app.route('/', methods=['GET', 'POST'])
def index():
    formupload = UploadForm()
    return render_template('index.html', formupload=formupload)


def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/event/new', methods=['GET', 'POST'])
@login_required
def post_events():
    formupload = UploadForm()
    if formupload.validate_on_submit():
        category = Category.query.get_or_404(
            formupload.category.data.id)
        title = formupload.title.data
        price = formupload.price.data
        address = formupload.address.data
        image = request.files['image']
        filename = ''
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))

        events = Event(title,
                       price,
                       address, category, filename)
        db.session.add(events)
        db.session.commit()
        flash('Event Posted!')
        return redirect(url_for('events_page', id=events.id))
    if formupload.errors:
        flash(formupload.errors, 'danger')

    return render_template('post_event.html', formupload=formupload)


@app.route('/event/<int:event_id>')
def event(event_id):
    _event = Event.query.get_or_404(event_id)
    return render_template('event_own.html', title=_event.title, _event=_event)  # specific event


@app.route("/event/<int:event_id>/update", methods=['GET', 'POST'])  # specific event edit
@login_required
def update_event(event_id):
    _event = Event.query.get_or_404(event_id)
    if _event.owner != current_user:
        abort(403)
    formupload = UploadForm()
    if formupload.validate_on_submit():
        _event.category = Category.query.get_or_404(
            formupload.category.data.id)
        _event.title = formupload.title.data
        _event.price = formupload.price.data
        _event.address = formupload.address.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', event_id=_event.id))
    elif request.method == 'GET':
        formupload.title.data = _event.title
        formupload.price.data = _event.price
        formupload.category.data.id = _event.category
        formupload.address = _event.address

    return render_template('edit_post.html', title='Update Event',
                           formupload=formupload, legend='Update Event')


@app.route("/event/<int:event_id>/delete", methods=['POST'])  # specific event delete
@login_required
def delete_event(post_id):
    _event = Event.query.get_or_404(post_id)
    if _event.owner != current_user:
        abort(403)
    db.session.delete(_event)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))


@app.route('/event', methods=['GET', 'POST'])  # main page for events
def events_page():
    event = Event.query.all()
    return render_template('event.html', event=event)


@app.route('/category-create', methods=['GET', 'POST'])
def create_category():  # admin stuff
    form = CategoryForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name)
        db.session.add(category)
        db.session.commit()
        flash('The category %s has been created' % name,
              'success')
        return redirect(url_for('post_events',
                                id=category.id))
    if form.errors: flash(form.errors)
    return render_template('category-create.html', form=form)


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


@app.errorhandler(403)
def no_permission(e):
    return render_template('403.html'), 403
