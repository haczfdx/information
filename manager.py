from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db
from info import models
from info.models import User

"""
'development'  开发环境配置
'production' 生产环境配置
'test' 测试环境配置
"""
app = create_app('production')

# 添加扩展命令行
manager = Manager(app)

# 数据库迁移
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.option('-n', '-name', dest="name")
@manager.option('-p', '-password', dest="password")
def createsuperuser(name, password):
    if not all([name, password]):
        print("参数不足")



    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

    print("添加成功")



if __name__ == '__main__':
    # print(app.url_map)
    manager.run()
