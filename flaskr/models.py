from flaskr import db
from flaskr import login_manager
from flask_login import UserMixin, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    picture_path = db.Column(db.Text)
    username = db.Column(db.String(60), index=True)
    email = db.Column(db.String(), unique=True, index=True)
    password = db.Column(db.String(64))
    profile_comment = db.Column(db.String(600))
    likes = db.relationship('PostLike', backref='users', lazy='dynamic')

    def __init__(self, username, email, password, picture_path=None):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.picture_path = picture_path

    def add_user(self):
        with db.session.begin(subtransactions=True):
            db.session.add(self)
        db.session.commit()

    @classmethod
    def select_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def validate_password(self, password):
        return check_password_hash(self.password, password)

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(user_id=self.id, post_id=post.id).delete()
    
    def has_liked_post(self, post):
        return PostLike.query.filter(PostLike.user_id == self.id, PostLike.post_id == post.id).count() > 0

    @classmethod
    def seach_by_username(cls, username):
        return cls.query.filter(
            cls.username.like(f'%{username}%'),
        ).with_entities(
            cls.id, cls.username, cls.picture_path,
        )


class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    picture_path = db.Column(db.Text)
    content = db.Column(db.String(600), index=True)
    user_id = db.Column(db.Integer)
    like_count = db.Column(db.Integer)
    author = db.Column(db.String())
    date_posted = db.Column(db.String())
    edit_count = db.Column(db.Integer)

    def __init__(self, picture_path, content, like_count, author, user_id, date_posted, edit_count):
        self.picture_path = picture_path
        self.content = content
        self.like_count = like_count
        self.author = author
        self.user_id = user_id
        self.date_posted = date_posted.strftime('%Y年%m月%d日')
        self.edit_count = edit_count

    def add_post(self):
        with db.session.begin(subtransactions=True):
            db.session.add(self)
        db.session.commit()

    def delete_post(self):
        with db.session.begin(subtransactions=True):
            db.session.delete(self)
        db.session.commit()

    @classmethod
    def search_by_content(cls, search_content):
        return cls.query.filter(
            cls.content.like(f'%{search_content}%'),
        ).with_entities(
            cls.id, cls.author, cls.picture_path, cls.content, cls.user_id, cls.like_count
        )


class PostLike(db.Model):

    __tablename__ = 'post_likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


class Comment(db.Model):

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(), index=True)
    content = db.Column(db.String(600), index=True)
    post_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __init__(self, author, content, post_id, user_id):
        self.author = author
        self.content = content
        self.post_id = post_id
        self.user_id = user_id

    def add_comment(self):
        with db.session.begin(subtransactions=True):
            db.session.add(self)
        db.session.commit()

    def delete_comment(self):
        with db.session.begin(subtransactions=True):
            db.session.delete(self)
        db.session.commit()