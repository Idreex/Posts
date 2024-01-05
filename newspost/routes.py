import os
import secrets
from datetime import datetime
from newspost import app, db, bcrypt, mail
from flask import render_template, redirect, flash, url_for, request, abort
from newspost.form import (RegistrationForm, LoginForm, UpdateAccountForm, PostForm,
                            UpdatePostForm, RequestResetForm, ResetPasswordForm)
from newspost.model import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
from flask_mail import Message





@app.route('/')
@app.route('/home')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
    


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
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post') 



@app.route('/post/<int:post_id>', methods=['GET','POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post = post)



@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = UpdatePostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', legend='Update Post', form=form)



@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))



@app.route('/user/<string:username>')
@login_required
def user_post(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=1)

    return render_template('user_post.html', title='Home', posts=posts, user=user)


def send_reset_email(user):
    token = user.generate_reset_password_code()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email]) 
    msg.body = f'''To reset your password, visit the following link: 
{url_for('reset_token',token=token, _external=True)}
If you did not make request for this, then kindly ignore this mail and no changes will be made
'''
    mail.send(msg)



@app.route('/reset/password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An Email has been sent to your mail, Please disregard it if you do not request', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html',title = 'Reset Password',form =form)

    
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.check_reset_password_code(token)
    if user is None:
        flash('That is an invalid or expired token', category='warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data)
        user.passwoed = hashed
        db.session.commit()
        flash(f'Account created successfully for {form.username.data}', 'success')
        return redirect(url_for('home'))
    return render_template('reset_token.html',title = 'Reset Password',form=form)


