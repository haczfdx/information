"""这个蓝图对应的是首页相关的操作"""
from flask import Blueprint

index_blue = Blueprint('index', __name__)

import info.moduels.index.views
