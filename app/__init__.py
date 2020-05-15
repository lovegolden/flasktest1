from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
#flask_mail.Mail实例对象
mail = Mail(app)
#数据库实例对象
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#用于保存用户登录设置
login = LoginManager(app)
#设置登录页面，用URL_UES()
login.login_view = 'login'

#非debug下进行日志传递邮箱和文件
if not app.debug:
    #mail_handler.setLevel(logging.ERROR)邮件级别设置为ERROR
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='love-golden@163.com',
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    #file_handler.setLevel(logging.INFO)日志文件级别设置为INFO
    #maxBytes日志文件大小为10KB，backupCount=10日志文件超过10KB后，生成新的文件，带扩展1.2.3
    #asctime为时间，levelname为事件名称，message信息，pathname路径名，lineno行号
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

from app import routes, models, errors

