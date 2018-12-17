from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db
from info import models

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

if __name__ == '__main__':
    # print(app.url_map)
    manager.run()