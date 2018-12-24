from _curses import flash
from datetime import datetime, timedelta
import time

from flask import render_template, request, jsonify, redirect, url_for, current_app, session, g, abort

from info import constants, db
from info.models import User, News, Category
from info.moduels.admin import admin_blue
from info.utils.common import user_login_status
from info.utils.image_storage import storage
from info.utils.response_code import RET


@admin_blue.route("/logout")
def logout():
    session.pop("mobile", None)
    session.pop("nick_name", None)
    session.pop("user_id", None)
    session.pop("is_admin", None)
    # print("123")
    return jsonify(errno=RET.PARAMERR, errmsg="退出成功")



@admin_blue.route('/news_type', methods=["GET", "POST"])
def news_type():
    """
    新闻的分类管理
    1、GET 查询数据 渲染模板
        - 查询数据库中除了最新以外的所有的分类
        - 循环遍历对象，生成列表字典
        - 将列表字典传到模板进行渲染
    2、POST 修改数据 Ajax局部刷新
        - 获取参数， id 和 name
        - 对发送过来的参数进行校验
        - 如果有id判断id是否在分类中，进行修改
        - 如果没有则添加数据

    :return:
    """
    if request.method == "GET":
        # 查询分类数据
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_type.html', errmsg="查询数据错误")

        category_dict_li = []
        for category in categories:
            # 取到分类的字典
            cate_dict = category.to_dict()
            category_dict_li.append(cate_dict)

        # 移除最新的分类
        category_dict_li.pop(0)

        data = {
            "categories": category_dict_li
        }

        return render_template('admin/news_type.html', data=data)

    # 新增或者添加分类
    # 1. 取参数
    cname = request.json.get("name")
    # 如果传了cid，代表是编辑已存在的分类
    cid = request.json.get("id")

    if not cname:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if cid:
        # 有 分类 id 代表查询相关数据
        try:
            cid = int(cid)
            category = Category.query.get(cid)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        if not category:
            return jsonify(errno=RET.NODATA, errmsg="未查询到分类数据")
        category.name = cname
    else:
        category = Category()
        category.name = cname
        db.session.add(category)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库出错")

    return jsonify(errno=RET.OK, errmsg="OK")


@admin_blue.route('/news_edit_detail', methods=["get", "post"])
def news_edit_detail():
    """
    新闻版式编辑
    1、GET 渲染模板
        - 获取get参数
        - 根据参数查询指定的NEWS
        - news_list.to_dict获取列表字典对象
        - 渲染模板， 传入处理后的数据进行模板渲染
    2、POST 处理数据
    :return:
    """
    if request.method == "GET":
        # 查询点击的新闻的相关数据并传入到模板中
        news_id = request.args.get("news_id")

        if not news_id:
            abort(404)

        try:
            news_id = int(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html', errmsg="参数错误")

        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html', errmsg="查询数据错误")

        if not news:
            return render_template('admin/news_edit_detail.html', errmsg="未查询到数据")

        # 查询分类数据
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html', errmsg="查询数据错误")

        category_dict_li = []
        for category in categories:
            # 取到分类的字典
            cate_dict = category.to_dict()
            # 判断当前遍历到的分类是否是当前新闻的分类，如果是，则添加is_selected为true
            if category.id == news.category_id:
                cate_dict["is_selected"] = True
            category_dict_li.append(cate_dict)

        # 移除最新的分类
        category_dict_li.pop(0)

        data = {
            "news": news.to_dict(),
            "categories": category_dict_li
        }

        return render_template('admin/news_edit_detail.html', data=data)

    # 取到Post进来的数据
    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    # 1.1 判断数据是否有值
    if not all([title, digest, content, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 查询指定id的
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 1.2 尝试读取图片
    if index_image:
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

        # 2. 将标题图片上传到七牛
        try:
            key = storage(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + key

    # 3. 设置相关数据
    news.title = title
    news.digest = digest
    news.content = content
    news.category_id = category_id

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库出错")

    return jsonify(errno=RET.OK, errmsg="OK")


@admin_blue.route("/news_edit")
def news_edit():
    """
    新闻的板式的编辑
    get 方式 渲染模板
    点击审核跳转页面
    :return:
    """
    # 获取参数
    page = request.args.get("p", 1)  # 获取args中的p参数的值
    keywords = request.args.get("keywords", None)
    pages = constants.ADMIN_USER_PAGE_MAX_COUNT  # 自己设置的每页显示的数量

    # 校验参数
    try:
        page = int(page)  # 对page进行校验，使用异常处理，如果出错设置默认值为1
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 处理参数
    # 先初始化参数，在发生异常的时候不会报错
    current_page = 1
    total_page = 1
    news = []

    filters = [News.status == 0]
    if keywords:
        filters.append(News.title.contains(keywords))

    # 数据库查询和分页操作
    try:
        paginate = News.query.filter(*filters).paginate(page, pages, False)
        news = paginate.items  # 得到的分页之后的列表对象
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 对user列表对象进行处理，生成字典列表，来方便模板的渲染
    news_dict_list = []
    for new in news:
        news_dict_list.append(new.to_basic_dict())

    data = {
        "news_dict_list": news_dict_list,
        "total_page": total_page,
        "current_page": current_page,
    }

    # 获取分页数据
    return render_template("admin/news_edit.html", data=data)


@admin_blue.route('/news_review_action', methods=["POST"])
def news_review_action():
    """
    新闻审核
    1. json获取参数
    2. 对参数进行校验
    3. 数据库查询指定ID新闻
    4. 根据action进行判断执行通过和不通过
    :return:
    """
    # 1. 获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 2. 参数校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询到指定的新闻数据
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    if action == "accept":
        # 代表接受
        news.status = 0

    else:
        # 代表拒绝
        reason = request.json.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="请输入拒绝原因")
        news.status = -1
        news.reason = reason

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库出错")


    return jsonify(errno=RET.OK, errmsg="OK")


@admin_blue.route("/news_review_detail/<int:news_id>")
def news_review_detail(news_id):
    # 通过id查询新闻
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return render_template('admin/news_review_detail.html', data={"errmsg": "未查询到此新闻"})

    # 返回数据
    data = {"news": news.to_dict()}
    return render_template('admin/news_review_detail.html', data=data)


@admin_blue.route("/news_review")
def news_review():
    """
    新闻审核页面
    get 方式 渲染模板
    点击审核跳转页面
    :return:
    """
    # 获取参数
    page = request.args.get("p", 1)  # 获取args中的p参数的值
    keywords = request.args.get("keywords", None)
    pages = constants.ADMIN_USER_PAGE_MAX_COUNT  # 自己设置的每页显示的数量

    # 校验参数
    try:
        page = int(page)  # 对page进行校验，使用异常处理，如果出错设置默认值为1
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 处理参数
    # 先初始化参数，在发生异常的时候不会报错
    current_page = 1
    total_page = 1
    news = []

    filters = [News.status != 0]
    if keywords:
        filters.append(News.title.contains(keywords))

    # 数据库查询和分页操作
    try:
        paginate = News.query.filter(*filters).paginate(page, pages, False)
        news = paginate.items  # 得到的分页之后的列表对象
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 对user列表对象进行处理，生成字典列表，来方便模板的渲染
    news_dict_list = []
    for new in news:
        news_dict_list.append(new.to_review_dict())

    data = {
        "news_dict_list": news_dict_list,
        "total_page": total_page,
        "current_page": current_page,
    }

    # 获取分页数据
    return render_template("admin/news_review.html", data=data)


@admin_blue.route("/user_list")
def user_list():
    """
    用户列表
    1. 获取查询的分类id
    2. 校验参数
    3. 渲染模板
    :return:
    """
    # 获取参数
    page = request.args.get("p", 1)  # 获取args中的p参数的值
    pages = constants.ADMIN_USER_PAGE_MAX_COUNT  # 自己设置的每页显示的数量

    # 校验参数
    try:
        page = int(page)  # 对page进行校验，使用异常处理，如果出错设置默认值为1
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 处理参数
    # 先初始化参数，在发生异常的时候不会报错
    users = []
    current_page = 1
    total_page = 1

    # 数据库查询和分页操作
    try:
        paginate = User.query.filter(User.is_admin == False).paginate(page, pages, False)
        users = paginate.items  # 得到的分页之后的列表对象
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 对user列表对象进行处理，生成字典列表，来方便模板的渲染
    user_dict_list = []
    for user in users:
        user_dict_list.append(user.to_admin_dict())

    data = {
        "user_dict_list": user_dict_list,
        "total_page": total_page,
        "current_page": current_page,
    }

    return render_template('admin/user_list.html', data=data)


@admin_blue.route("/user_count")
def user_count():
    """
    用户页面统计人数
    :return:
    """

    # 总人数
    total_count = 0

    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 月新增人数
    mon_count = 0

    now_time = time.localtime()
    # print(now_time.tm_year)
    mon_begin_time = datetime.strptime("%d-%02d-01" % (now_time.tm_year, now_time.tm_mon), "%Y-%m-%d")
    # print(mon_begin_time)
    try:
        # mon_count = User.query.filter( User.create_time > mon_begin_time).count()
        mon_count = User.query.filter(User.is_admin == False, User.create_time > mon_begin_time).count()
    except Exception as e:
        current_app.logger.error(e)

    # 日新增人数
    day_count = 0
    now_time = time.localtime()
    # 获取今天的开始时间， 12-23 0.0.0
    day_begin_time = datetime.strptime("%d-%02d-%02d" % (now_time.tm_year, now_time.tm_mon, now_time.tm_mday),
                                       "%Y-%m-%d")
    # print(day_begin_time)
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_time).count()
    except Exception as e:
        current_app.logger.error(e)

    # 循环进行添加30天之内的数据
    # 两个数据，一个是时间，还有一个是活跃数
    active_time = []
    active_count = []
    # 取出30天之前一直到今天的日期
    for i in range(30, -1, -1):
        # 取到某一天的0点0分
        begin_date = day_begin_time - timedelta(days=i)
        # 取到下一天的0点0分
        end_date = day_begin_time - timedelta(days=(i - 1))
        count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                  User.last_login < end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime('%Y-%m-%d'))

    # print(active_time)
    # print(active_count)

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_time": active_time,
        "active_count": active_count
    }
    return render_template("admin/user_count.html", data=data)


@admin_blue.route("index")
@user_login_status
def index():
    user = g.user
    if not user:
        return redirect(url_for("index.index"))

    data = {
        "user_dict": user.to_admin_dict() if user else None
    }

    return render_template("admin/index.html", data=data)


@admin_blue.route("/login", methods=["post", "get"])
def login():
    """
    后台页面的制作
    :return:
    """
    if request.method == "GET":
        is_admin = session.get("is_admin", False)
        user_id = session.get("user_id", None)
        if is_admin and user_id:
            return redirect(url_for("admin.index"))
        return render_template("admin/login.html")

    # 获取参数
    username = request.form.get("username")
    password = request.form.get("password")

    # 判断参数
    if not all([username, password]):
        return render_template('admin/login.html', errmsg="参数错误")

    # 查询当前用户是否是管理员
    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="数据库出错")

    if not user:
        return render_template('admin/login.html', errmsg="未查询到用户信息")

    # 校验密码
    if not user.check_passoword(password):
        return render_template('admin/login.html', errmsg="用户名或者密码错误")

    # 保存用户的登录信息
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["is_admin"] = user.is_admin

    return redirect(url_for("admin.index"))
