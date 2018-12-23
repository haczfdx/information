from flask import render_template, request, jsonify, redirect, url_for

from info.moduels.admin import admin_blue
from info.utils.response_code import RET


@admin_blue.route("index")
def admin_index():
    return render_template("admin/index.html")


@admin_blue.route("/login", methods=["post", "get"])
def admin_login():
    """
    后台页面的制作
    :return:
    """
    if request.method == "GET":
        return render_template("admin/login.html")

    # 获取参数
    username = request.form.get("username")
    password = request.form.get("password")

    # 校验参数
    if not all([username, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    return redirect(url_for("admin.index"))
