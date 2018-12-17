from flask import request

from info import constants
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

    # print(nav_list)

    # category_list = []
    # try:
    #     class_id = request.args.get("class_id", 1)
    #     category = Category.query.filter(Category.id == class_id).first()
    #     category_list_obj = category.news_list.limit(constants.HOME_PAGE_MAX_NEWS).all()
    #
    # except Exception as e:
    #
    #     current_app.logger.error(e)
    # else:
    #     for cate in category_list_obj:
    #         category_list.append(cate.to_basic_dict())

    # 定义一个data字典存放数据
    # print(category_list[0])





