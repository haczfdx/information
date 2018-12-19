"""定义一个自定义的工具扩展"""
import functools

from flask import session, current_app, g, jsonify, abort

from info import db
from info.models import User
from info.utils.response_code import RET


def rank_class(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"


def user_login_status(f):
    """
    @functools.wraps
        这个装饰器可以将被装饰的函数中的__name__的值保持不变，不然会变成装饰器内置函数的名称
        这个装饰器主要是解决了flask中使用装饰路由使用了__name__，所以必须要保证这个__name__的值是唯一的
    :param f:
    :return:
    """
    @functools.wraps(f)
    def wapper(*args, **kwargs):
        user_id = session.get("user_id")  # 通过user_id来取出user的值
        user = None
        if user_id:
            try:
                user = User.query.filter(User.id == user_id).first()  # 只有在取到值得前提下才去查询
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return f(*args, **kwargs)
    return wapper


def commit(json=True, status=404):
    # 手动提交数据
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        if json:
            return jsonify(errno=RET.OK, errmsg="数据提交错误")
        else:
            abort(status)
