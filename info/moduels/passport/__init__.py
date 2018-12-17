"""这个蓝图对应的是登录注册相关的操作"""
from flask import Blueprint

passport_blue = Blueprint('passport', __name__)

import info.moduels.passport.views
