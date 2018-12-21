"""这个蓝图对应的是登录注册相关的操作"""
from flask import Blueprint

user_blue = Blueprint('user', __name__)

import info.moduels.user.views
