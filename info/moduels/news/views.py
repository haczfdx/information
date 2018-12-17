from flask import request, jsonify, current_app
from info import constants
from info.models import Category, News
from info.utils.response_code import RET
from . import news_blue


@news_blue.route("list")
def index_list():
    """
    实现主页的分类的显示
    1、获取一下必须的参数，每页显示的个数，当前的分类，当前的分类的编号
        思路：
            可以通过args的方式传送过来当前的分类编号
            每页的显示个数可以通过constants常量来获取
            页码的制作（当前页，总页码）
                每一页显示的个数，当前分类的总量/每页显示个数可以取得一共有多少页
    2. 根据参数来向数据库请求信息
    3. 根据请求的信息在模板中进行渲染
    :return:
    """

    # 获取分类的编号，如果用户没有get数据那么默认分类的编号就是最近
    class_cid = request.args.get("class_cid", 1)
    home_max_news = constants.HOME_PAGE_MAX_NEWS

    class_cid = int(class_cid)


    all_news_list = []
    try:
        # 先查询一下最新的数据
        if class_cid == 1:
            news_list = News.query.order_by(News.create_time.desc()).limit(home_max_news).all()
        else:
            news_list = Category.query.filter(class_cid == Category.id).first().news_list.limit(home_max_news).all()
        print(news_list)
    except Exception as e:
        current_app.logger.error(e)
    else:
        # 遍历一下每一个对象，获取
        for news in news_list:
            all_news_list.append(news.to_basic_dict())
            # print(news.to_basic_dict())

    # print(all_news_list)

    return jsonify(errno=RET.OK, errmsg=all_news_list)
