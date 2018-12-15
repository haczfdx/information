from logging.handlers import RotatingFileHandler
import logging
import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from config import config

db = SQLAlchemy()

# 初始化redis对象
redis_store = None


def create_app(config_name):
    """工厂模式抽出业务逻辑配置"""
    # 配置日志
    setup_log(config_name)

    # 创建app实例,__name__为当前目录的名称，在外部导入的时候回区别，在当前文件中就是__main__
    app = Flask(__name__)

    # 加载配置文件

    app.config.from_object(config[config_name])

    # 配置mysql数据库
    db.init_app(app)

    # 配置redis数据库
    global redis_store  # 使用全局redis
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT, decode_responses=True)

    # 开启CSRF保护
    # CSRFProtect(app)
    #
    # # 设置Session保存的位置
    Session(app)

    # 进行蓝图的注册
    from info.moduels.index import index_blue

    app.register_blueprint(index_blue, url_prefix="/")
    from info.moduels.passport import passport_blue

    app.register_blueprint(passport_blue, url_prefix="/passport")

    return app


def setup_log(config_name):
    """配置日志, 注意这里的logging模块就是python自带的日志模块"""
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
