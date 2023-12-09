from flask import render_template, flash, url_for, redirect
from newspost import app, db, bcrypt, login_manager
from newspost.form import RegistrationForm, Login
from newspost.model import User, Post
from flask_login import login_user, current_user, login_required, logout_user




@app.route('/')
@app.route('/home')
def home():
    if not current_user.is_authenticated:
        return redirect('login')
    return render_template('home.html', title = 'Home' )



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f"{user.username} logged in successfully", 'success')
            return redirect(url_for('home'))
    return render_template('login.html',title = 'Login', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password = hashed)
        db.session.add(user)
        db.session.commit()
        flash(f'Account successfully created by {form.username.data}', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title = 'Register', form=form)


@app.route('/about')
@login_required
def about():
    return render_template('about.html', title = 'About')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('home')


@app.route ('/account')
def account():

    return render_template('account.html', title='Account')

