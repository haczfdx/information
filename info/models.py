"""创建数据库模型"""
from datetime import datetime
# from info import db
# from info import create_app, db
# app = create_app('test')

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)


class Config():
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app.config.from_object(Config)
db = SQLAlchemy(app)


# 用户表
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    nick_name = db.Column(db.String(64), unique=True)  # 昵称
    avater_url = db.Column(db.String(256))  # 头像的URL地址
    mobile = db.Column(db.SmallInteger, unique=True)  # 手机号码
    password_hash = db.Column(db.String(64))  # hash加密之后的密码
    last_login = db.Column(db.DateTime, index=True, default=datetime.now)  # 最后一次的登录时间
    is_admin = db.Column(db.Boolean, default=False)  # 判断是否是管理员
    signature = db.Column(db.String(512))  # 个性签名
    gender = db.Column(db.Enum('man', 'woman'), default='man')




# 新闻表
class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(256))  # 新闻标题
    source = db.Column(db.SmallInteger)  # 新闻评分
    index_image_url = db.Column(db.String(256), )  # 主页图片的URL地址
    create_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 新闻的创建时间
    digest = db.Column(db.String(256))  # 新闻摘要
    clicks = db.Column(db.Integer)  # 新闻的点击次数
    content = db.Column(db.Text)  # 新闻的内容
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # 一个外键关联到分类表中
    user_id = db.Column(db.Integer, unique=True)  # 用户ID


# 新闻的分类表
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(64), unique=True)  # 新闻分类名称
    newss = db.relationship('News', backref='category', lazy='dynamic')


# 评论表
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('news.user_id'))  # 用户id
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))  # 用户id
    create_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 评论的创建时间
    content = db.Column(db.Text)  # 评论的
    partent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))  # 父级评论id
    like_count = db.Column(db.Integer)  # 点赞的人数
    comments = db.relationship('Comment', backref='child_id', lazy="dynamic")
    users = db.relationship('User', backref= db.backref('comment_s', lazy="dynamic"),
                            secondary='commentlike',
                            lazy='dynamic')


# 评论点赞
class CommentLike(db.Model):
    __tablename__ = 'commentlike'
    comment_id = db.Column(db.Integer, primary_key=True)  # 评论的ID
    user_id = db.Column(db.Integer, primary_key=True)  # 用户的ID


db.drop_all()
db.create_all()
