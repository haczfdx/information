function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    var news_id = $(this).attr("news_id")

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    })

    // 收藏
    $(".collection").click(function () {
        var news_id = $(this).attr("news_id")
        param = {
            "news_id": news_id,
            "avtive": "collection"
        }

        $.ajax({
            url: "/news/news_collect",
            type: "POST",
            contentType: "application/json",
            headers: {
                'X-CSRFToken': getCookie("csrf_token")
            },
            data: JSON.stringify(param),
            success: function (response) {
                if (response.errno == 0) {
                    // 代表请求数据成功执行
                    location.reload()
                    // alert(response.errmsg)
                } else if (response.errno == 4102) {
                    $('.login_form_con').show()
                } else {
                    // 请求失败
                    alert(response.errmsg)
                }


            }
        })


    })

    // 取消收藏
    $(".collected").click(function () {
        var news_id = $(this).attr("news_id")
        param = {
            "news_id": news_id,
            "avtive": "collected"
        }

        $.ajax({
            url: "/news/news_collect",
            type: "POST",
            contentType: "application/json",
            headers: {
                'X-CSRFToken': getCookie("csrf_token")
            },
            data: JSON.stringify(param),
            success: function (response) {
                if (response.errno == 0) {
                    // 代表请求数据成功执行
                    // alert(response.errmsg)
                    location.reload()
                } else {
                    // 请求失败
                    alert(response.errmsg)
                }


            }
        })

    })

    // 评论提交
    $(".comment_form").submit(function (e) {
        var comment_text = $(".comment_input").val()
        var news_id = $(".comment_form").attr("news_id")
        param = {
            'comment_text': comment_text,
            'news_id': news_id
        }
        e.preventDefault();
        $.ajax({
            url: "/news/news_comment_add",
            type: "POST",
            contentType: "application/json",
            headers: {"X-CSRFToken": getCookie("csrf_token")},
            data: JSON.stringify(param),
            success: function (response) {
                if (response.errno == 0) {
                    // 请求成功
                    // alert(response.errmsg)
                    location.reload()

                }else if (response.errno == 4102) {
                    $('.login_form_con').show()
                }

                else {
                    // 请求失败
                    alert(response.errmsg)
                }

            }
        })
    })

    $('.comment_list_con').delegate('a,input', 'click', function () {

        var sHandler = $(this).prop('class');

        if (sHandler.indexOf('comment_reply') >= 0) {
            $(this).next().toggle();
        }

        if (sHandler.indexOf('reply_cancel') >= 0) {
            $(this).parent().toggle();
        }

        if (sHandler.indexOf('comment_up') >= 0) {
            var $this = $(this);
            if (sHandler.indexOf('has_comment_up') >= 0) {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                $this.removeClass('has_comment_up')
            } else {
                $this.addClass('has_comment_up')
            }
        }

        if (sHandler.indexOf('reply_sub') >= 0) {
               // e.preventDefault();
            // alert()
             var comment_text = $(this).prev().val()
        var news_id = $(this).attr("news_id")
            var parent_id = $(this).attr("parent_id")
            // alert(parent_id)
        param = {
            'comment_text': comment_text,
            'news_id': news_id,
            'parent_id': parent_id
        }

        //      alert("123")
        $.ajax({
            url: "/news/news_comment_add",
            type: "POST",
            contentType: "application/json",
            headers: {"X-CSRFToken": getCookie("csrf_token")},
            data: JSON.stringify(param),
            success: function (response) {
                if (response.errno == 0) {
                    // 请求成功
                    // alert(response.errmsg)
                    location.reload()

                }else if (response.errno == 4102) {
                    $('.login_form_con').show()
                }

                else {
                    // 请求失败
                    alert(response.errmsg)
                }

            }
        })
        }
    })

    // 关注当前新闻作者
    $(".focus").click(function () {

        var news_user_id = $(this).attr("news_user_id")
        // alert(news_user_id)
        var param={
            'news_user_id': news_user_id
        }
        $.ajax({
            url:"news/follower_user",
            type:"post",
            data:JSON.stringify(param),
            headers:{
                'X-CSRFToken': getCookie('csrf-token')
            },
            success: function (response) {


            }

        })
    })

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    })
})