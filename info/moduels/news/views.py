from flask import request, jsonify, current_app, render_template, abort, session, g
from info import constants, db
from info.models import Category, News, User, Comment, CommentLike
from info.utils.common import user_login_status, commit
from info.utils.response_code import RET
from . import news_blue


@news_blue.route("/comment_like", methods=["POST"])
@user_login_status
def comment_like():
    """
    用户点赞的后端处理逻辑
    1. 获取用户数据
    2. 获取传送过来的数据
    3. 校验参数
    4. 处理数据
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="你还没有登录")

    # 获取参数
    # news_id = request.json.get("user_id")
    comment_id = request.json.get("comment_id")
    is_like = request.json.get("is_like")

    try:
        # news_id = int(news_id)
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error("非法参数")
        return jsonify(errno=RET.DATAERR, errmsg="非法参数")

    # print(user_id)
    # print(comment_id)
    # print(is_like)

    # if not all([news_id, comment_id]):
    #     current_app.logger.error("非法参数")
    #     return jsonify(errno=RET.DATAERR, errmsg="非法参数")

    # print(user.id)
    # print(user_id)
    # if user.id != user_id:
    #     current_app.logger.error("非法操作")
    #     return jsonify(errno=RET.DATAERR, errmsg="非法操作")

    # 查询出对应的评论
    comment = None
    try:
        comment = Comment.query.filter(comment_id == Comment.id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="非法查询数据")

    # 前面的所有信息校验成功，下面开始操作点赞和取消点赞的操作
    if is_like:
        # 进行用户与点赞之间的关联
        try:
            commentliket = CommentLike()
            commentliket.user_id = user.id
            commentliket.comment_id = comment_id
            db.session.add(commentliket)
            db.session.commit()
            comment.like_count += 1
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据添加出错")
    else:
        try:
            CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                     CommentLike.user_id == user.id).delete()
            comment.like_count -= 1
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据删除出错")
    #  计算点赞的数量


    try:
        # comment.like_count = CommentLike.query.filter(CommentLike.comment_id == comment_id).count()
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="点赞修改出错")

    return jsonify(errno=RET.OK, errmsg="OK")


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
    parent_id = request.json.get("parent_id")

    # print(news_id)
    # print(comment_text)
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
            return jsonify(errno=RET.NODATA, errmsg="评论错误，没有这个新闻")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库链接错误")

    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = comment_text
    comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库提交出错")

    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict())


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

    # 查询当前新闻的所有的评论

    comments = []
    try:
        comments = news.comments.order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comments_list = []

    for comment in comments:
        comment_dict = comment.to_dict()
        # 判断当前用户是否点赞这个评论
        is_commentlike = False
        # 取出当前用户所有的点赞
        if user:
            # if (user.id == comment.user_id) and \
            #         (CommentLike.query.filter(CommentLike.comment_id == comment.id,
            #                                   CommentLike.user_id == user.user_id).first()):
            if user and CommentLike.query.filter(CommentLike.comment_id == comment.id,
                                                 CommentLike.user_id == user.id).first():
                is_commentlike = True

        comment_dict["is_commentlike"] = is_commentlike

        comments_list.append(comment_dict)

    # 判断新闻是否被收藏
    is_collection = False
    if user:
        if news in user.collection_news:
            is_collection = True

    # 判断当前的用户是否被关注
    is_followered = False
    if user:
        if news:
            if news.to_dict()["author"]:
                # print(news.to_dict()["author"]['id'])
                if news.to_dict()["author"]["id"] in user.followers:
                    is_followered = True

    # 新闻的点击次数加一
    news.clicks += 1
    commit(json=False)

    data = {
        'user_dict': user.to_dict() if user else None,
        'news_data': news.to_dict() if news else None,
        'news_list': news_list,
        "is_collection": is_collection,
        'comments_list': comments_list,
        'is_followered': is_followered,
        'is_commentlike': is_commentlike
    }

    return render_template("news/detail.html", data=data)
