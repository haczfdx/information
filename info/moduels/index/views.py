from info import constants
from info.models import User, News, Category
from . import index_blue
from flask import render_template, current_app, session, request


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

    # 获取当前导航
    nav_info_list = []
    try:
        nav_list = Category.query.all()  # 查询出所有的导航栏

    except Exception as e:
        current_app.logger.error(e)
    else:
        for nav in nav_list:
            nav_info_list.append(nav.to_dict())
            # print(nav.to_dict())

    # print(nav_info_list)


    data = {
        'user_dict': user_dict,
        'news_list': news_list,
        'nav_info_list': nav_info_list

    }
    # 'category_list': category_list
    # print(category_list)

    return render_template('news/index.html', data=data)


@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file('news/favicon.ico')
