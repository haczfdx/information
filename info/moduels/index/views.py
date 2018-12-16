from . import index_blue
from flask import render_template, current_app, session


@index_blue.route("/")
def index():
    # 通过session来判断现在是否登录
    print(session)


    return render_template('news/index.html')


@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file('news/favicon.ico')
