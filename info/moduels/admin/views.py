from _curses import flash

from flask import render_template, request, jsonify, redirect, url_for, current_app, session

from info.models import User
from info.moduels.admin import admin_blue
from info.utils.response_code import RET


@admin_blue.route("index")
def index():
    return render_template("admin/index.html")


@admin_blue.route("/login", methods=["post", "get"])
def login():
    """
    后台页面的制作
    :return:
    """
    if request.method == "GET":
        is_admin = session.get("is_admin", False)
        user_id = session.get("user_id", None)
        if is_admin and user_id:
            return redirect(url_for("admin.index"))
        return render_template("admin/login.html")

    # 获取参数
    username = request.form.get("username")
    password = request.form.get("password")

    # 判断参数
    if not all([username, password]):
        return render_template('admin/login.html', errmsg="参数错误")

    # 查询当前用户是否是管理员
    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="数据库出错")

    if not user:
        return render_template('admin/login.html', errmsg="未查询到用户信息")

    # 校验密码
    if not user.check_passoword(password):
        return render_template('admin/login.html', errmsg="用户名或者密码错误")

    # 保存用户的登录信息
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["is_admin"] = user.is_admin

    return redirect(url_for("admin.index"))
