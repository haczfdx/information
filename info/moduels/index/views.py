from info import constants
from info.models import User, News
from . import index_blue
from flask import render_template, current_app, session


@index_blue.route("/")
def index():
    # 通过session来判断现在是否登录
    user_id = session.get("user_id")  # 通过user_id来取出user的值
    user_dict = None
    if user_id:
        user = User.query.filter(User.id == user_id).first()  # 只有在取到值得前提下才去查询
        user_dict = user.to_admin_dict()

    """主页的右侧的排行"""
    # 数据库查询排行之后的数据，只取出配置中显示个数的值

    news_list = []
    news_rank_info = None
    try:
        news_rank_info = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)

    if news_rank_info:
        for news_info in news_rank_info:
            news_list.append(news_info.title)
        # print(news_list)

    # 定义一个data字典存放数据
    data = {
        'user_dict': user_dict,
        'news_list': news_list
    }

    return render_template('news/index.html', data=data)


@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file('news/favicon.ico')
