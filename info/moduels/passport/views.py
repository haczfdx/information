import random
import re
from datetime import datetime

from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.response_code import RET
from . import passport_blue
from info import redis_store, constants, db
from flask import request, abort, make_response, current_app, jsonify, session
from info.utils.captcha.captcha import captcha


@passport_blue.route("/logout")
def logout():
    session.pop("mobile", None)
    session.pop("nick_name", None)
    session.pop("user_id", None)
    return jsonify(errno=RET.PARAMERR, errmsg="退出成功")


@passport_blue.route("/login", methods=["POST"])
def login():
    """登录的ajax接口"""

    # 第一步老规矩解析post数据
    mobile = request.json.get("mobile")
    password = request.json.get("password")
    # 判断所有的值是否有空值，如果有空直接return走
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数发生错误")

    # 对手机号进行正则匹配，不符合要求直接返回
    if not re.match(r"^1[345678]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的电话号码")

    # 开始进入数据库拉数据进行匹配
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库链接出错")

    if not user:
        # 用户名输入错误
        return jsonify(errno=RET.LOGINERR, errmsg="请输入正确的用户名")

    if not user.check_passoword(password):
        return jsonify(errno=RET.LOGINERR, errmsg="密码错误")

    # 已经验证成功用户名和密码了，开始修改最后一次的登录的时候

    user.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="不知道为啥登录时间出错了")

    # 登录成功先设置会话的session
    session["user_id"] = user.id
    session["moblie"] = user.mobile
    session["nick_name"] = user.nick_name
    # session.permanent = True  # 设置session的过期时间为自己设置的选项

    return jsonify(errno=RET.OK, errmsg="OK")


@passport_blue.route("/register", methods=["POST"])
def register():
    """实现用户在注册按钮点击之后实现的接口"""
    # print(request.json)

    # 先表单数据传送过来的所有的值
    mobile = request.json.get("mobile")
    smscode = request.json.get("smscode")
    password = request.json.get("password")

    # 判断所有的值是否有空值，如果有空直接return走
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数发生错误")

    # 对手机号进行正则匹配，不符合要求直接返回
    if not re.match(r"^1[345678]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的电话号码")

    # 通过手机号码去redis中取出对应的数据进行判断
    try:
        redis_sms_code = redis_store.get("sms_" + mobile)
        # print("手机验证码为：", redis_sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="这个手机号码没有发送验证码")

    # 很重要的一步，进行手机验证码的校验
    if not redis_sms_code:
        return jsonify(error=RET.DATAERR, errmsg="验证码已经过期了")
    if redis_sms_code != smscode:
        return jsonify(error=RET.DATAERR, errmsg="手机验证码是咋了，匹配不正确")

    # 对密码的位数进行匹配，暂时的要求至少得有6位
    if len(password) < 6:
        return jsonify(errno=RET.PARAMERR, errmsg="密码至少要输入6位以上")

    # 能走到这步很明显成功满足所有的条件了，下面进行mysql添加用户的功能
    user = User()
    user.mobile = mobile  # 用户的手机
    user.nick_name = mobile  # 用户的昵称，可以使用手机先代替
    user.password = password  # 用户的密码
    user.last_login = datetime.now()  # 先初始化登录时间
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="用户名已经被注册")

    # 终于走到这里了，注册成功将注册写入会话session
    session["user_id"] = user.id
    session["moblie"] = mobile
    session["nick_name"] = user.nick_name
    # session.permanent = True  # 设置session的过期时间为自己设置的选项

    return jsonify(errno=RET.OK, errmsg="OK")


@passport_blue.route("/sms_code", methods=["POST"])
def send_sms_code():
    """
    接口需要获取，手机号，图片验证码的内容，URL中的编号
    取出redis的内容与用户的验证码内容进行校验
    如果对比不一致，那么返回验证码输入错误
    一致的话，生成验证码的内容，发送过去
    :return:
    """
    # 做测试的时候使用
    # return jsonify(errno=RET.OK, errmsg="发送成功")

    # 1、将参数提取出来
    # params_dict = json.loads(request.data)
    params_dict = request.json

    mobile = params_dict.get("mobile")
    image_code = params_dict.get("imageCode")
    image_code_id = params_dict.get("image_code_id")
    # print(mobile)
    # print(image_code)
    # print(image_code_id)
    # 2、进行数据的校验（判断是否有值，是否符合规则）
    if not all([mobile, image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数发生错误")
    # 对手机号进行正则匹配，不符合要求直接返回
    if not re.match(r"^1[345678]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的电话号码")

    # 通过image_code_id 取出数据验证码与填写的验证码进行匹配
    try:
        # print("imageCode_" + image_code_id)
        redis_image_code = redis_store.get("imageCodeId_" + image_code_id)
        # print("验证码：", redis_image_code)
    except Exception as e:
        current_app.logger.error(e)
        # return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的电话号码")
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    # 说明没有查询到数据
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已经过期")

    if redis_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 生成一个6位数的随机数
    authcode = "%06d" % random.randint(0, 999999)
    # print("手机验证码是：", authcode)
    current_app.logger.debug("手机的验证码是：" + str(authcode))

    # # 下面实现验证码的功能，这里已经测试成功就暂时不给手机发送，直接打印出验证码
    # result = CCP().send_template_sms(mobile, [authcode, int(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)
    # if result:
    #     current_app.logger.error("手机验证发送出错")
    #     return jsonify(errno=RET.THIRDERR, errmsg="手机验证码发送失败")

    # 将发送的随机验证填写到redis数据库中，key为sms_手机号，value值为验证码
    try:
        redis_store.set("sms_" + mobile, authcode, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="手机验证码数据保存失败")

    # 所有的都OK了，发送验证码
    return jsonify(errno=RET.OK, errmsg="发送成功")


@passport_blue.route("/image_code")
def get_image_code():
    """
    生成图片验证并返回
    1.从request.agrs中取出值
    2.要判断这个参数是否请求正确
    3.生成图片验证码
    :return:
    """
    # 从request中取出值如果没有值那就是请求出错，抛出403的错误
    image_code_id = request.args.get('imageCodeId', None)
    if not image_code_id:
        return abort(403)

    # 通过api接口获取验证的内容和image的文件      
    name, text, image = captcha.generate_captcha()
    current_app.logger.debug("验证码是：" + text)

    # 将验证的内容写入redis的数据库，缓存时间为300秒
    # print(type(image_code_id))
    # print(text)
    try:
        redis_store.set("imageCodeId_" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)




    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response
