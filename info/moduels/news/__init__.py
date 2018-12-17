"""这个蓝图对应的是首页相关的操作"""
from flask import Blueprint

news_blue = Blueprint('news', __name__)

import info.moduels.news.views
