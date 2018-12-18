from info import constants
from info.models import User, News, Category
from info.utils.common import user_login_status
from info.utils.response_code import RET
from . import index_blue
from flask import render_template, current_app, session, request, jsonify, g


@index_blue.route("news_list")
def news_list():
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

    # 1. 获取参数
    class_id = request.args.get("class_id", "1")  # 分类ID
    page = request.args.get("page", "1")  # 当前页
    # page_all_data = request.args.get("page_all_data", 10)  # 每一页显示的数量
    per_page = constants.HOME_PAGE_MAX_NEWS  # 每一页显示的数量

    # 校验参数，请求过来的参数必须是数值类型的数据
    try:
        class_id = int(class_id)
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="参数出错")

    query_list = []
    if class_id != 1:
        # 如果不是查询最新的那么就要append查询参数，参数参数为列表，可以在filter中前面加*解包
        query_list.append(News.category_id == class_id)
    try:
        paginate = News.query.filter(*query_list).order_by(News.create_time.desc()).paginate(page, per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    # 相当于执行了.limit(per_page).offset(per_page*(page-1)).all()
    news_obj_list = paginate.items  # 获取所有的页面对象
    all_page = paginate.pages  # 总页数
    current_page = paginate.page  # 当前页

    # 获取出每一个的内容数据添加到列表中返回
    news_list = []
    for news in news_obj_list:
        news_list.append(news.to_basic_dict())

    data = {
        'all_page': all_page,
        'current_page': current_page,
        'news_list': news_list
    }

    return jsonify(errno=RET.OK, errmsg="获取数据成功", data=data)


@index_blue.route("/")
@user_login_status
def index():
    # 通过session来判断现在是否登录
    user = g.user

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
    if nav_list:
        for nav in nav_list:
            nav_info_list.append(nav.to_dict())
            # print(nav.to_dict())

    # print(nav_info_list)

    data = {
        'user_dict': user.to_admin_dict() if user else  None,
        'news_list': news_list,
        'nav_info_list': nav_info_list

    }
    # 'category_list': category_list
    # print(category_list)

    return render_template('news/index.html', data=data)


@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file('news/favicon.ico')
