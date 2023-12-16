import os
import secrets
from datetime import datetime
from newspost import app,db
from flask import render_template, redirect, flash, url_for, request, abort
from newspost.form import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, UpdatePostForm
from newspost.model import User, Post
from newspost import bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image




@app.route('/')
@app.route('/home')
@login_required
def home():

    posts = Post.query.all()

    return render_template('home.html', title='Home', posts=posts)





@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('home')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created successfully for {form.username.data}', 'success')
        return redirect('home')

    return render_template('register.html', title='Register', form=form)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('home')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('home')
        else:
            flash('Login unsuccessful')
    return render_template('login.html', title='Login', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('login')


@app.route('/about')
@login_required
def about():
    return render_template('about.html', title='about')



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            try:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            except Exception:
                flash('Picture extention not supported', 'danger')
                return redirect(url_for('account'))
        try:
            if form.username.data == current_user.username and form.email.data == current_user.email:
                flash('No changes made','info')
                return redirect('account')
        except Exception:
            flash('No changes made', 'info')
           
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)




@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', title='New Post', form=form, legend='New Post') 



@app.route('/post/<int:post_id>', methods=['GET','POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post = post)



@app.route('/post/<int:post_id>/update', methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)
    form = UpdatePostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.date_posted = datetime.utcnow()
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('Update_post.html', form=form, title='Update Post', legend='Update Post')



@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect('home')










