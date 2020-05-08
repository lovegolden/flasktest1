from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#用于保存用户登录设置
login = LoginManager(app)
#设置登录页面，用URL_UES()
login.login_view = 'login'

from app import routes, models