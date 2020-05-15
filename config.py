import os

#D:\flask\flask
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #sqlite:///D:\flask\flask\app.db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    #数据库更新时，不通知app
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 错误日志发送邮箱，不知道QQ邮箱，因为QQ邮箱只要用SSL协议，SMTPHandler不支持SSL
    # MAIL_SERVER邮箱服务器
    # MAIL_PORT端口
    # MAIL_PORT，TLS协议
    # MAIL_USERNAME，邮箱
    # MAIL_PASSWORD，短信授权码
    # ADMINS，收邮箱列表
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = "love-golden@163.com"
    MAIL_PASSWORD = "GBIZUICBXHLHUEPK"
    ADMINS = ['love-golden@163.com']

    #post分页，每页显示3个post
    POSTS_PER_PAGE = 3