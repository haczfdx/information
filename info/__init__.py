import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from config import Config

# 创建app实例,__name__为当前目录的名称，在外部导入的时候回区别，在当前文件中就是__main__
app = Flask(__name__)

# 加载配置文件
app.config.from_object(Config)


# 配置mysql数据库
db = SQLAlchemy(app)

# 配置redis数据库
redis_conn = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 开启CSRF保护
CSRFProtect(app)
#
# # 设置Session保存的位置
Session(app)
