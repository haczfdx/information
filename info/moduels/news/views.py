from flask import request, jsonify, current_app, render_template, abort, session, g
from info import constants
from info.models import Category, News, User
from info.utils.common import user_login_status
from info.utils.response_code import RET
from . import news_blue


@news_blue.route("/<int:news_id>")
@user_login_status
def news_details(news_id):
    """
    获取新闻的详情页面
    :param news_id:
        根据news_id来获取获取数据库的内容在details的模板中进行渲染
    :return:
    """
    # 通过session来判断现在是否登录，可以通过全局G变量来存储
    user = g.user

    # 从数据库中提取出指定news的数据
    try:
        news = News.query.filter(News.id == news_id).first()
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

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
            news_list.append(news_info.to_review_dict())

    data = {
        'user_dict': user.to_admin_dict() if user else None,
        'news_data': news.to_dict() if news else None,
        'news_list': news_list
    }

    return render_template("news/detail.html", data=data)
