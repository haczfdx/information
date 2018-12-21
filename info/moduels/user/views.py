from flask import render_template, g, request, jsonify, current_app, redirect, url_for
from werkzeug.datastructures import FileStorage

from info import db
from info import constants
from info.moduels.user import user_blue
from info.utils.common import user_login_status
from info.utils.image_storage import storage
from info.utils.response_code import RET





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



@user_blue.route("/user_pass_info", methods=["GET", 'POST'])
@user_login_status
def user_pass_info():
    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="你还没有登录")

    if request.method == "GET":
        data = {
            "user_dict": user.to_dict() if user else None
        }
        return render_template("news/user_pass_info.html", data=data)

    old_pwd = request.json.get("old_pwd")
    new_pwd1 = request.json.get("new_pwd1")
    new_pwd2 = request.json.get("new_pwd2")

    # 1. 判断是否为空如果是空直接返回
    if not all([old_pwd, new_pwd1, new_pwd2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数发生错误")

    if new_pwd1 != new_pwd2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码输入不相同")

    if len(new_pwd1)<6:
        return jsonify(errno=RET.PARAMERR, errmsg="密码不可以小于6位")

    if not user.check_passoword(old_pwd):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的密码")

    try:
        user.password = new_pwd1
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作数据库出错")

    return jsonify(errno=RET.OK, errmsg="OK")





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

    # 获取参数
    try:
        file = request.files.get("avatar").read()  # type:FileStorage
        print(len(file))
        if len(file) > constants.USER_AVATAR_SIZE:
            return jsonify(errno=RET.PARAMERR, errmsg="不可以上传大于1M的图片")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="文件有错误")

    # 开始上传七牛云
    try:
        file_key = storage(file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="文件上传失败")

    try:
        user.avatar_url = file_key
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作数据库出错")

    data= {
        'avatar_url': constants.QINIU_DOMIN_PREFIX+file_key
    }
    return jsonify(errno=RET.OK, errmsg="OK", data=data)


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
