from flask import render_template, g

from info.moduels.user import user_blue
from info.utils.common import user_login_status


@user_blue.route("/user_pic_info", methods=["GET", 'POST'])
@user_login_status
def user_pic_info():
    return render_template("news/user_pic_info.html")




@user_blue.route("/user_pass_info", methods=["GET", 'POST'])
@user_login_status
def user_pass_info():
    return render_template("news/user_pass_info.html")


@user_blue.route("/user_news_release", methods=["GET", 'POST'])
@user_login_status
def user_news_release():
    return render_template("news/user_news_release.html")


@user_blue.route("/user_news_list", methods=["GET", 'POST'])
@user_login_status
def user_news_list():
    return render_template("news/user_news_list.html")



@user_blue.route("/user_follow", methods=["GET", 'POST'])
@user_login_status
def user_follow():
    return render_template("news/user_follow.html")




@user_blue.route("/user_collection", methods=["GET", 'POST'])
@user_login_status
def user_collection():
    return render_template("news/user_collection.html")


@user_blue.route("/user_base_info", methods=["GET", 'POST'])
@user_login_status
def user_base_info():
    return render_template("news/user_base_info.html")


@user_blue.route("/")
@user_login_status
def index():
    user = g.user
    data = {
        'user_dict': user.to_dict() if user else None
    }
    return render_template("news/user.html", data=data)
