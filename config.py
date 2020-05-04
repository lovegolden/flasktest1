import os

#basedir = os.path.abspath(os.path.dirname(__file__))

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
#D:\flask\flask\db_repository
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
#D:\flask\flask
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #sqlite:///D:\flask\flask\app.db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    #数据库更新时，不通知app
    SQLALCHEMY_TRACK_MODIFICATIONS = False