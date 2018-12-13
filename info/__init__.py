import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from config import config

db = SQLAlchemy()


def create_app(config_name):
    """工厂模式抽出业务逻辑配置"""
    # 创建app实例,__name__为当前目录的名称，在外部导入的时候回区别，在当前文件中就是__main__
    app = Flask(__name__)

    # 加载配置文件

    app.config.from_object(config[config_name])

    # 配置mysql数据库
    db.init_app(app)

    # 配置redis数据库
    redis_conn = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)

    # 开启CSRF保护
    CSRFProtect(app)
    #
    # # 设置Session保存的位置
    Session(app)

    return app
