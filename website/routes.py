import os

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from website import app, ALLOWED_EXTENSIONS
from website import db
from website.form import RegisterForm, SearchForm, UploadForm, LoginForm, CategoryForm, EditProfileForm
from website.model import User, Event, Category, Role, Music


#@app.before_first_request
#def create_db():
#    db.drop_all()
#    db.create_all()
#    role_user = Role(role_name="User")
#    role_owner = Role(role_name="Event Owner")
#    category_1 = Category(name="Club")
#    category_2 = Category(name="Restaurant")
#    category_3 = Category(name="Cafe")
#    db.session.add_all([category_1, category_2, category_3])
#    db.session.add_all([role_user, role_owner])
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
        searched = form.searched.data
        category = form.category.data.name
        # Query the Database
        events = events.filter(Event.title.like('%' + searched + '%'))
        # category_name = Event.category
        events = events.filter(Event.category.has(name=category))
        # events = events.filter(Event.)
        events = events.order_by(Event.title).all()

        return render_template("search.html",
                               form=form,
                               searched=searched,
                               events=events)


# AUTHORIZATION
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        password_hash = form.password.data
        new_user = User(
                name=form.name.data,
                family_name=form.family_name.data,
                username=form.username.data,
                mail=form.mail.data,
                password=password_hash,
                role=Role.query.get_or_404(
                    form.role.data.id),
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


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    role = User.query.filter_by(role_id=current_user.role_id).first_or_404()

    posts = [
        {'author': user, 'body': 'Test post #1', 'role': role},
        {'author': user, 'body': 'Test post #2'}
    ]

    if user.role_id == 2:
        events = user.owned_events()
        print(events)
        return render_template('event_owner.html', events=events)
    else:
        return render_template('user.html', user=user, posts=posts,role=role)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.family_name = form.family_name.data
        current_user.username = form.username.data
        current_user.mail = form.mail.data

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.family_name.data = current_user.family_name
        form.username.data = current_user.username
        form.mail.data = current_user.mail
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


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
    owner = User.query.filter_by(role_id=current_user.role_id).first_or_404()
    if owner.role_id != 2:
        abort(403)
    formupload = UploadForm()
    event_owner = current_user.username
    formupload.organizer.data = event_owner
    if formupload.validate_on_submit():
        owner = event_owner
        category = Category.query.get_or_404(
            formupload.category.data.id)
        music_type = Music.query.get_or_404(
            formupload.music_type.data.id
        )
        title = formupload.title.data
        price = formupload.price.data
        address = formupload.address.data
        image = request.files['image']
        filename = ''
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))

        events = Event(owner,title,
                       price,
                       address, category, music_type, filename)
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
    return render_template('show_event.html', title=_event.title, _event=_event)  # specific event


@app.route("/event/<int:event_id>/update", methods=['GET', 'POST'])  # specific event edit
@login_required
def update_event(event_id):
    _event = Event.query.get_or_404(event_id)

    if _event.owner != current_user.username:
        abort(403)
    formupload = UploadForm()
    if formupload.validate_on_submit():
        _event.category = Category.query.get_or_404(
            formupload.category.data.id)
        _event.title = formupload.title.data
        _event.price = formupload.price.data
        _event.address = formupload.address.data
        _event.music = Music.query.get_or_404(
            formupload.music_type.data.id
        )
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post_events'))
    elif request.method == 'GET':
        formupload.title.data = _event.title
        formupload.price.data = _event.price
        formupload.category.data = _event.category
        # formupload.music.data = _event.music
        formupload.address.data = _event.address
        formupload.event_id = event_id
        formupload.organizer.data = _event.owner

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


@app.route('/event/followed', methods=['GET', 'POST'])
@login_required
def followed_event_page():
    # events = current_user.followed_posts().all()
    events = current_user.liked_posts()
    return render_template('event_followed.html', events=events)


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

@app.route('/event/<int:event_id>/like', methods=['GET'])
def like_event(event_id):
    _event = Event.query.get_or_404(event_id)
    if current_user.like(_event):
        flash('Liked event!', 'success')
    else:
        flash('You already liked this post', 'warning')
    return redirect(url_for('events_page'))

@app.route('/event/<int:event_id>/unlike', methods=['GET'])
def unlike_event(event_id):
    _event = Event.query.get_or_404(event_id)
    current_user.unlike(_event)
    flash('Unliked event!', 'success')
    return redirect(url_for('events_page'))

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
