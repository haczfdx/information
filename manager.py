from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from info import create_app, db
from info import  models

app = create_app('test')

# 进行脚本化
manager = Manager(app)

# 设置数据库迁移
Migrate(db, app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
