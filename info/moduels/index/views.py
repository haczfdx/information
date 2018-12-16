from info.models import User
from . import index_blue
from flask import render_template, current_app, session


@index_blue.route("/")
def index():
    # 通过session来判断现在是否登录
    user_id = session.get("user_id") # 通过user_id来取出user的值
    user = None
    data = None
    if user_id:
        user = User.query.filter(User.id == user_id).first() # 只有在取到值得前提下才去查询
        data = user.to_admin_dict()





    return render_template('news/index.html', data=data)


@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file('news/favicon.ico')

