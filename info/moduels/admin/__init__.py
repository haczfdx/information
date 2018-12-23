"""这个蓝图对应的是首页相关的操作"""
from flask import Blueprint

admin_blue = Blueprint('admin', __name__)

import info.moduels.admin.views
