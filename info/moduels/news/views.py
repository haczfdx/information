from flask import request, jsonify, current_app, render_template, abort, session, g
from info import constants, db
from info.models import Category, News, User, Comment
from info.utils.common import user_login_status, commit
from info.utils.response_code import RET
from . import news_blue


@news_blue.route("/news_comment_add", methods=["POST"])
@user_login_status
def news_comment_add():
    """
    用户提交评论的接口
    1. 获取参数
    2. 校验参数
    3. 返回JSON数据
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="你还没有登录")

    # print(request.args)
    news_id = request.json.get("news_id")
    comment_text = request.json.get("comment_text")

    print(news_id)
    print(comment_text)
    # 校验参数
    if not all([news_id, comment_text]):
        current_app.logger.error("非法参数")
        return jsonify(errno=RET.DATAERR, errmsg="非法参数")

    # 可以在这边控制评论字的数量比如200字
    if len(comment_text) > 200:
        return jsonify(errno=RET.DATAERR, errmsg="字数不能超过200字")

    # 读取出对应新闻的数据
    try:
        news = News.query.filter(News.id == news_id).first()
        if not news:
            return jsonify(errno=RET.NODATA, errmsg="收藏出错，没有这个新闻")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库链接错误")

    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = comment_text

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库提交出错")

    return jsonify(errno=RET.OK, errmsg="OK")


@news_blue.route("/news_collect", methods=["POST"])
@user_login_status
def news_collect():
    """
    1. 获取POST数据
    2. 校验数据
    3. 返回json数据，页面进行处理
    :return:
    """
    # 获取参数
    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="你还没有登录")

    # print(request.args)
    news_id = request.json.get("news_id")
    avtive = request.json.get("avtive")

    # 校验参数
    if not all([news_id, avtive]):
        current_app.logger.error("非法参数")
        return jsonify(errno=RET.DATAERR, errmsg="非法参数")

    try:
        news = News.query.filter(News.id == news_id).first()
        if not news:
            return jsonify(errno=RET.NODATA, errmsg="收藏出错，没有这个新闻")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库链接错误")

    # print(user.collection_news.all())
    if avtive == "collection":
        if news not in user.collection_news.all():
            user.collection_news.append(news)
        else:
            return jsonify(errno=RET.DBERR, errmsg="收藏失败, append失败")
    elif avtive == "collected":
        if news in user.collection_news.all():
            user.collection_news.remove(news)
        else:
            return jsonify(errno=RET.DBERR, errmsg="移除失败, remove失败")

    commit()

    return jsonify(errno=RET.OK, errmsg="ok")


@news_blue.route("/<int:news_id>")
@user_login_status
def news_details(news_id):
    """
    获取新闻的详情页面
    :param news_id:
        根据news_id来获取获取数据库的内容在details的模板中进行渲染
    :return:
    """

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

    # 判断新闻是否被收藏
    is_collection = False
    if user:
        if news in user.collection_news:
            is_collection = True

    # 查询当前新闻的所有的评论

    comments = []
    try:
        comments = news.comments.order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comments_parent_list = []
    comments_child_list = []
    # print(comments[0].to_dict())
    for comment in comments:
        if comment.to_dict()["parent"]:
            """这样就是父类的评论"""
            comments_child_list.append(comment.parent)
        else:
            comments_parent_list.append(comment.to_dict())

    print(comments_parent_list)
    print(comments_child_list)
        # comments_list.append(comment.to_dict())

    # 新闻的点击次数加一
    news.clicks += 1
    commit(json=False)

    data = {
        'user_dict': user.to_dict() if user else None,
        'news_data': news.to_dict() if news else None,
        'news_list': news_list,
        "is_collection": is_collection,
        'comments_parent_list': comments_parent_list,
        'comments_child_list': comments_child_list

    }

    return render_template("news/detail.html", data=data)
