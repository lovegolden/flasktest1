#flask db init 数据库初始化化
#flask db migrate -m "users table" 数据库迁移，生成下一级数据库（最新数据库）
#flask db upgrade 升级数据库
#flask db downgrade 降级数据库，一般不用
#VISION1


from app import create_app, db
from app.models import User, Post
if __name__ == "__main__":
    app = create_app()
    app.run()
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'Post': Post}
