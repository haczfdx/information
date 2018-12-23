"""这个蓝图对应的是首页相关的操作"""
from flask import Blueprint, session, request, url_for, redirect

admin_blue = Blueprint('admin', __name__)

import info.moduels.admin.views


@admin_blue.before_request
def check_admin():
    """
    在登录admin相关的目录请求之前判断session，进行跳转
    1. 必须是管理员
    2. 只要不是LOGIN页面
    :return:
    """
    is_admin = session.get('is_admin', False)
    if not is_admin and not request.url.endswith(url_for("admin.login")):
        return redirect(url_for("index.index"))


