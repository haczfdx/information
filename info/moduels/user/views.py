from flask import render_template, g, request, jsonify, current_app, redirect, url_for, abort
from werkzeug.datastructures import FileStorage

from info import db
from info import constants
from info.models import Category, News, User
from info.moduels.user import user_blue
from info.utils.common import user_login_status
from info.utils.image_storage import storage
from info.utils.response_code import RET



@user_blue.route("/other_info", methods=["GET", 'POST'])
@user_login_status
def other_info():

    user = g.user

    # 去查询其他人的用户信息
    other_id = request.args.get("user_id")

    if not other_id:
        abort(404)

    # 查询指定id的用户信息
    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)

    if not other:
        abort(404)

    is_followed = False
    # if 当前新闻有作者，并且 当前登录用户已关注过这个用户
    if other and user:
        # if user 是否关注过 news.user
        if other in user.followed:
            is_followed = True

    data = {
        "is_followed": is_followed,
        "user_dict": g.user.to_dict() if g.user else None,
        "other_info": other.to_dict()
    }
    return render_template('news/other.html', data=data)



@user_blue.route("/user_follow")
@user_login_status
def user_follow():
    """
    用户列表中的已关注的用户列表
    1. 使用GET的方式去获取数据
    2. 使用paginate来进行查询分页
        获取当前页所有用户对象
        获取当前页
        获取总页数
    3. 返回数据渲渲渲染模板
    :return:
    """

    # 获取页数
    p = request.args.get("p", 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    # 取到当前登录用户
    user = g.user

    follower_users = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.followed.paginate(p, constants.USER_FOLLOWED_MAX_COUNT, False)
        # 获取当前页数据
        follower_users = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    follower_users_list = []

    for follow_user in follower_users:
        follower_users_list.append(follow_user.to_dict())

    data = {
        "follower_users_list": follower_users_list,
        "total_page": total_page,
        "current_page": current_page
    }

    return render_template('news/user_follow.html', data=data)


@user_blue.route("/user_news_list")
@user_login_status
def user_news_list():
    """
    发布的新闻列表

    :return:
    """
    if not g.user:
        return "请登录"
    # 获取参数
    page = request.args.get("p", 1)

    # 判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    user = g.user
    # 初始化参数
    news_list = []
    current_page = 1
    total_page = 1
    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    data = {
        "news_dict_list": news_dict_list,
        "total_page": total_page,
        "current_page": current_page,
    }
    return render_template("news/user_news_list.html", data=data)


@user_blue.route("/user_news_release", methods=["GET", 'POST'])
@user_login_status
def user_news_release():
    if request.method == "GET":
        try:
            categorys = Category.query.filter(Category.name != "最新").all()
        except Exception as e:
            current_app.logger.error(e)
            abort(404)

        category_list = []
        for category in categorys:
            category_list.append(category.to_dict())

        data = {
            "category_list": category_list,
        }
        return render_template("news/user_news_release.html", data=data)

    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="请登录")

    # 标题
    title = request.form.get("title")
    # 新闻来源
    source = "个人发布"
    # 摘要
    digest = request.form.get("digest")
    # 新闻内容
    content = request.form.get("content")
    # 索引图片
    index_image = request.files.get("index_image")
    # 分类id
    category_id = request.form.get("category_id")

    print(title)
    print(digest)
    print(content)
    print(index_image)
    print(category_id)

    # 不可以为空
    if not all([title, source, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 对传过来的参数进行转换成int类型
    try:
        category_id = int(category_id)
        if category_id == 0:
            return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 取到图片，将图片上传到七牛云
    try:
        index_image_data = index_image.read()
        # 上传到七牛云
        key = storage(index_image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 新闻表添加数据
    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = g.user.id
    # 审核状态
    news.status = 1

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="OK")


@user_blue.route("/user_collection")
@user_login_status
def user_collection():
    """
    用户的收藏页面
    1. 获取参数
        - 当前页
    2. 返回数据
        - 当前页
        - 总页数
        - 每页的数据
    :return:
    """
    user = g.user
    if not user:
        return "请先登录"

    # 获取当前页
    page = request.args.get('p', 1)
    page_show = constants.USER_COLLECTION_MAX_NEWS

    # 校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        # return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        abort(404)

    try:
        user_collection = user.collection_news.paginate(page, page_show)
        currentPage = user_collection.page
        totalPage = user_collection.pages
        items = user_collection.items
    except Exception as e:
        current_app.logger.error(e)
        # return jsonify(errno=RET.DBERR, errmsg="数据库查询出错")
        abort(404)

    user_collection_list = []
    for item in items:
        user_collection_list.append(item.to_review_dict())

    data = {
        'currentPage': currentPage,
        'totalPage': totalPage,
        'user_collection_list': user_collection_list
    }
    return render_template("news/user_collection.html", data=data)


@user_blue.route("/user_pass_info", methods=["GET", 'POST'])
@user_login_status
def user_pass_info():
    """
    修改密码
    :return:
    """
    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="密码错误")

    old_pwd = request.json.get("old_pwd")
    new_pwd1 = request.json.get("new_pwd1")
    new_pwd2 = request.json.get("new_pwd2")

    # 1. 判断是否为空如果是空直接返回
    if not all([old_pwd, new_pwd1, new_pwd2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数发生错误")

    if new_pwd1 != new_pwd2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码输入不相同")

    if len(new_pwd1) < 6:
        return jsonify(errno=RET.PARAMERR, errmsg="密码不可以小于6位")

    if not user.check_passoword(old_pwd):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的密码")

    try:
        user.password = new_pwd1
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作数据库出错")

    return jsonify(errno=RET.OK, errmsg="OK")


@user_blue.route("/user_pic_info", methods=["GET", 'POST'])
@user_login_status
def user_pic_info():
    if request.method == "GET":
        data = {
            "user_dict": g.user.to_dict() if g.user else None
        }
        return render_template("news/user_pic_info.html", data=data)

    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="密码错误")
    # 获取参数
    try:
        file = request.files.get("avatar").read()  # type:FileStorage
        # print(len(file))
        if len(file) > constants.USER_AVATAR_SIZE:
            return jsonify(errno=RET.PARAMERR, errmsg="不可以上传大于1M的图片")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="文件有错误")

    # 开始上传七牛云
    try:
        file_key = storage(file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="文件上传失败")

    try:
        user.avatar_url = file_key
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作数据库出错")

    data = {
        'avatar_url': constants.QINIU_DOMIN_PREFIX + file_key
    }
    return jsonify(errno=RET.OK, errmsg="OK", data=data)


@user_blue.route("/user_base_info", methods=["GET", 'POST'])
@user_login_status
def user_base_info():
    """
    get 请求渲染模板
    post进行数据处理
    :return:
    """

    if request.method == "GET":
        user = g.user
        if not user:
            return "请先登录"

        data = {
            "user_dict": user.to_dict() if user else None
        }
        return render_template("news/user_base_info.html", data=data)

    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="请登录")

    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")

    # 1. 判断是否为空如果是空直接返回
    if not all([nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数发生错误")

    # 个性签名进行校验
    if len(signature) > 50:
        return jsonify(errno=RET.PARAMERR, errmsg="个性签名必须小于50个字")

    # 用户昵称
    if len(nick_name) > 20:
        return jsonify(errno=RET.PARAMERR, errmsg="用户名称必须小于10个字")

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg="性别填写错误")

    try:
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作数据库出错")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())


@user_blue.route("/")
@user_login_status
def index():
    user = g.user
    if not user:
        return redirect(url_for("index.index"))
    data = {
        'user_dict': user.to_dict() if user else None
    }
    return render_template("news/user.html", data=data)
