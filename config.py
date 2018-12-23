import logging
import os
import redis
from base64 import b64encode


class Config(object):
    """项目的配置文件的父类"""
    # 配置一些app的基础的设置
    ENV = ""
    DEBUG = True
    SECRET_KEY = b64encode(os.urandom(64))

    """配置一些数据库的信息"""
    # MySQL数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 可以配置自动Commit

    # Redis的配置
    REDIS_PORT = 6379
    REDIS_HOST = '127.0.0.1'

    """安全配置"""
    # session的配置
    SESSION_TYPE = 'redis'  # 指定session保存到redis中
    SESSION_USE_SIGNER = True  # 让cookie中的session_id被加密处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    SESSION_PERMANENT = False
    # SESSION_REDIS = redis.StrictRedis(port=REDIS_PORT, host=REDIS_HOST)  # 设置为redis实例

    PERMANENT_SESSION_LIFETIME = 86400 * 2  # 设置有效期，单位是秒

    """日志相关的配置"""
    # 日志的级别
    LOG_LEVEL = logging.DEBUG


class DvelopMentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    LOG_LEVEL = logging.ERROR


class TestingConfig(Config):
    """测试环境配置"""
    pass


config = {
    'development': DvelopMentConfig,
    'production': ProductionConfig,
    'test': TestingConfig

}
