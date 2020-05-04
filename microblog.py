#flask db init 数据库初始化化
#flask db migrate -m "users table" 数据库迁移，生成下一级数据库（最新数据库）
#flask db upgrade 升级数据库
#flask db downgrade 降级数据库，一般不用
#VISION1


from app import app
app.run()
