from flask import render_template, g, request, jsonify, current_app, redirect, url_for

from info import db
from info.moduels.user import user_blue
from info.utils.common import user_login_status
from info.utils.response_code import RET


@user_blue.route("/user_pass_info", methods=["GET", 'POST'])
@user_login_status
def user_pass_info():
    return render_template("news/user_pass_info.html")


@user_blue.route("/user_news_release", methods=["GET", 'POST'])
@user_login_status
def user_news_release():
    return render_template("news/user_news_release.html")


@user_blue.route("/user_news_list", methods=["GET", 'POST'])
@user_login_status
def user_news_list():
    return render_template("news/user_news_list.html")


@user_blue.route("/user_follow", methods=["GET", 'POST'])
@user_login_status
def user_follow():
    return render_template("news/user_follow.html")


@user_blue.route("/user_collection", methods=["GET", 'POST'])
@user_login_status
def user_collection():
    return render_template("news/user_collection.html")


@user_blue.route("/user_pic_info", methods=["GET", 'POST'])
@user_login_status
def user_pic_info():
    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="你还没有登录")

    if request.method == "GET":
        data = {
            "user_dict": user.to_dict() if user else None
        }
        return render_template("news/user_pic_info.html", data=data)


@user_blue.route("/user_base_info", methods=["GET", 'POST'])
@user_login_status
def user_base_info():
    """
    get 请求渲染模板
    post进行数据处理
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="你还没有登录")

    if request.method == "GET":
        data = {
            "user_dict": user.to_dict() if user else None
        }
        return render_template("news/user_base_info.html", data=data)

    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")

    # 1. 判断是否为空如果是空直接返回
    if not all([nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数发生错误")

    # 个性签名进行校验
    if len(signature) > 50:
        return jsonify(errno=RET.PARAMERR, errmsg="个性签名必须小于50个字")

    # 用户昵称
    if len(nick_name) > 20:
        return jsonify(errno=RET.PARAMERR, errmsg="用户名称必须小于10个字")

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg="性别填写错误")

    try:
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作数据库出错")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())


@user_blue.route("/")
@user_login_status
def index():
    user = g.user
    if not user:
        return redirect(url_for("index.index"))
    data = {
        'user_dict': user.to_dict() if user else None
    }
    return render_template("news/user.html", data=data)
