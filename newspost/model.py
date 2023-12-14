from datetime import datetime
from newspost import db
from sqlalchemy import Column, DateTime, String, ForeignKey, Integer, Text
from flask_login import UserMixin
from newspost import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True , nullable=False)
    username = db.Column(db.String(60),unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    image_file = db.Column(db.String, default='default.jpg')
    post = db.relationship('Post', backref='author', lazy=True)


    def __repr__(self):
        return f'{self.username}, {self.email}, {self.password}'
    


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(60),unique=True, nullable=False)
    content = db.Column(db.Text(420), nullable=False, unique=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



    def __repr__(self):
        return f'{self.title}, {self.date_posted}'
    



