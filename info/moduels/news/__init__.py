"""这个蓝图对应的是新闻页面的相关的操作"""
from flask import Blueprint

news_blue = Blueprint('news', __name__)

import info.moduels.news.views
