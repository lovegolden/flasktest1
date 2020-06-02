
from datetime import datetime
from app import db,login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from flask import current_app

#多对多辅助表，关注其他用户
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

#用户表
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #向gravatar请求用户头像图片，digest为用户邮箱hash码，size为图像像素，网站默认是80*80，可设置为128*128，size传128
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    #判断是否关注该用户，>0等价于True
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    #如果没关注，就关注该用户
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    #取消关注该用户
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    #把关注者的post和自己的post，以时间倒序（最近时间)向用户展现
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    #邮箱验证密码连接，expires_in=600有效时间10分钟，app.config['SECRET_KEY']密匙，algorithm='HS256'加密算法
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    #staticmethod类的静态方法，可直接调用，不用传类参
    #解密邮箱验证密码，返回字典app.config['SECRET_KEY']
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)

#微博表
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


#把函数load_user(id)作为参数传递到login.user_loader函数中
#以ID号检索用户对象
@login.user_loader
def load_user(id):
    return User.query.get(int(id))