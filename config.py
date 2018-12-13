import os
import redis
from base64 import b64encode


class Config(object):
    """项目的配置文件的父类"""
    # 配置一些app的基础的设置
    DEBUG = True
    SECRET_KEY = b64encode(os.urandom(64))

    """配置一些数据库的信息"""
    # MySQL数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis的配置
    REDIS_PORT = 6739
    REDIS_HOST = 'localhost'

    """安全配置"""
    # CSRF安全配置
    # CSRFProtect

    # session的配置
    SESSION_TYPE = 'redis'  # 配置会话为redis
    SESSION_USE_SIGNER = True  # 设置加上安全秘钥
    SESSION_REDIS = redis.StrictRedis(port=REDIS_PORT, host=REDIS_HOST)  # 设置为redis对象
    PERMANM_SESSION_LIFETIME = 86400  # 设置有效期，单位是秒


class DvelopentConfig(Config):
    """开发环境配置"""
    pass


class ProductionConfig(Config):
    """生产环境配置"""
    pass


class TestingConfig(Config):
    """测试环境配置"""
    pass
