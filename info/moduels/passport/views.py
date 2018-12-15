import random
import re

from info.libs.yuntongxun.sms import CCP
from info.utils.response_code import RET
from . import passport_blue
from info import redis_store, constants
from flask import request, abort, make_response, current_app, jsonify
from info.utils.captcha.captcha import captcha


@passport_blue.route("/sms_code", methods=["POST"])
def send_sms_code():
    """
    接口需要获取，手机号，图片验证码的内容，URL中的编号
    取出redis的内容与用户的验证码内容进行校验
    如果对比不一致，那么返回验证码输入错误
    一致的话，生成验证码的内容，发送过去
    :return:
    """
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
        print("imageCode_" + image_code_id)
        redis_image_code = redis_store.get("imageCodeId_" + image_code_id)
        print(redis_image_code)
    except Exception as e:
        current_app.logger.error(e)
        # return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的电话号码")
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    # 说明没有查询到数据
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已经过期")

    if redis_image_code != image_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 生成一个6位数的随机数
    authcode = "%06d" % random.randint(0, 999999)
    print(authcode)
    ccp = CCP()
    # 注意： 测试的短信模板编号为1
    ccp.send_template_sms(mobile, [authcode, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)
    # 3、先从redis中取出真实的验证码
    # 4、进行验证码的校对
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
    current_app.logger.error("验证码是：" + text)

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
