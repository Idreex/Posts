from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from newspost.model import User
from flask_login import current_user



class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='Sign up')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(f'{username.data} is taken already, try other username')
        


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(f'{email.data} is taken already')
        


class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    remember = BooleanField(label='Remember me')
    submit = SubmitField(label='Login')



class UpdateAccountForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    picture = FileField(label='Upload Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField(label='Update')



    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('The name is taken, choose different name')


    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('The Email is taken already, try other one')


class PostForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    content = TextAreaField(label='Content', validators=[DataRequired()])
    submit = SubmitField(label='Create Post')


class UpdatePostForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    content = TextAreaField(label='Content', validators=[DataRequired()])
    submit = SubmitField(label='Update Post')


class RequestResetForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    submit = SubmitField(label='Request password Reset ')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError('There is no account for this user, Please sign up first')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField(label='Password', validators=[DataRequired()])
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='Reset Password')
