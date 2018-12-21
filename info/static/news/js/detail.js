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
                    // location.reload()
                    $(".collection").hide()
                    $(".collected").show()
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
                    // location.reload()
                     $(".collection").show()
                    $(".collected").hide()
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

        var params = {
            'comment_text': comment_text,
            'news_id': news_id
        }
        e.preventDefault();
        $.ajax({
            url: "/news/news_comment_add",
            type: "POST",
            contentType: "application/json",
            headers: {"X-CSRFToken": getCookie("csrf_token")},
            data: JSON.stringify(params),
            success: function (response) {
                if (response.errno == 0) {
                    // 请求成功
                    // alert(response.errmsg)
                    // location.reload()
                    console.log(response.data)
                    var comments = response.data

                    if (comments.user.this_avatar_url) {
                        var avatar_url = '../../static/news/images/headImage/' + comments.user.this_avatar_url
                    } else {
                        var avatar_url = '../../static/news/images/worm.jpg'
                    }


                    var new_comment =
                        '<div class="comment_list">' +
                        '<div class="person_pic fl">' +
                        '<img src="' + avatar_url + '" alt="用户图标">' +
                        '</div>' +
                        '<div class="user_name fl">' + comments.user.nick_name + '</div>' +
                        '<div class="comment_text fl">' +
                        comments.content +
                        '</div>' +
                        '<div class="comment_time fl">' + comments.create_time + '</div>' +
                        '<a news_id="'+comments.news_id+'" comment_id="'+comments.id+'" href="javascript:;" class="comment_up has_comment_up fr">' + comments.like_count + '</a>' +
                        '<a href="javascript:;" class="comment_reply fr">回复</a>' +
                        '<from class="reply_form fl">' +
                        '<textarea class="reply_input"></textarea>' +
                        '<input type="submit" name="" value="回复" class="reply_sub fr" parent_id="' + comments.id + '"' +
                        'news_id="' + comments.news_id + '">' +
                        '<input type="reset" name="" value="取消" class="reply_cancel fr">' +
                        '</from>' +
                        '</div>'


                    // alert(new_comment_1)


                    // $(".comment_count").after(new_comment)

                    $(".comment_list_con").prepend(new_comment)
                        $(".comment_input").val("")
                    // alert("1232")
                    UpNumComment()

                } else if (response.errno == 4102) {
                    $('.login_form_con').show()
                } else {
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

                // alert("取消点赞")
               var comment_id = $this.attr('comment_id')
                var user_id = $this.attr('user_id')
                var params = {
                    'comment_id':comment_id,
                    'user_id': user_id,
                    'is_like': false
                }
                $.ajax({
                    url: "/news/comment_like",
                    type: "POST",
                    contentType: "application/json",
                    headers:{"X-CSRFToken": getCookie("csrf_token")},
                    data: JSON.stringify(params),
                    success: function (response) {
                        if(response.errno==0){
                            // 成功
                             $this.removeClass('has_comment_up')
                            $this.html(Number($this.html())-1)
                        }else if (response.errno == 4102) {
                            $('.login_form_con').show()
                        }else {
                            // 失败
                            alert(response.errmsg)
                        }

                    }
                })

            } else {

                // alert("点赞")
                var comment_id = $this.attr('comment_id')
                var user_id = $this.attr('user_id')

                var params = {
                    'comment_id':comment_id,
                    'user_id': user_id,
                    'is_like': true
                }
                $.ajax({
                    url: "/news/comment_like",
                    type: "POST",
                    contentType: "application/json",
                    headers:{"X-CSRFToken": getCookie("csrf_token")},
                    data: JSON.stringify(params),
                    success: function (response) {
                        if(response.errno==0){
                            // 成功
                            $this.addClass('has_comment_up')
                            $this.html(Number($this.html())+1)
                        }else if (response.errno == 4102) {
                            $('.login_form_con').show()
                        }else {
                            // 失败
                             alert(response.errmsg)
                        }

                    }
                })
            }
        }

        if (sHandler.indexOf('reply_sub') >= 0) {
            // e.preventDefault();
            // alert()
            var comment_text = $(this).prev().val()
            var news_id = $(this).attr("news_id")
            var parent_id = $(this).attr("parent_id")
            var $this = $(this)
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
                        // location.reload()
                        var comments = response.data
                        if (comments.user.this_avatar_url) {
                            var avatar_url = '../../static/news/images/headImage/' + comments.user.this_avatar_url
                        } else {
                            var avatar_url = '../../static/news/images/worm.jpg'
                        }


                        var new_comment =
                            '<div class="comment_list">' +
                            '<div class="person_pic fl">' +
                            '<img src="' + avatar_url + '" alt="用户图标">' +
                            '</div>' +
                            '<div class="user_name fl">' + comments.user.nick_name + '</div>' +
                            '<div class="comment_text fl">' +
                            comments.content +
                            '</div>' +
                                '<div class="reply_text_con fl">'+
                                    '<div class="user_name2">@'+ comments.parent.user.nick_name +'</div>'+
                                    '<div class="reply_text">'+
                                         comments.parent.content +
                                    '</div>'+
                                '</div>'+
                            '<div class="comment_time fl">' + comments.create_time + '</div>' +
                            '<a news_id="'+comments.news_id+'" comment_id="'+comments.id+'"  href="javascript:;" class="comment_up has_comment_up fr">' + comments.like_count + '</a>' +
                            '<a  href="javascript:;" class="comment_reply fr">回复</a>' +
                            '<from class="reply_form fl">' +
                            '<textarea class="reply_input"></textarea>' +
                            '<input type="submit" name="" value="回复" class="reply_sub fr" parent_id="' + comments.id + '"' +
                            'news_id="' + comments.news_id + '">' +
                            '<input type="reset" name="" value="取消" class="reply_cancel fr">' +
                            '</from>' +
                            '</div>'



                        // $(".comment_count").after(new_comment)
                        $(".comment_list_con").prepend(new_comment)

                        $this.prev().val("")
                        $this.parent().hide()
                        // alert(2134)
                        UpNumComment()

                    } else if (response.errno == 4102) {
                        $('.login_form_con').show()
                    } else {
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
        var param = {
            'news_user_id': news_user_id
        }
        $.ajax({
            url: "news/follower_user",
            type: "post",
            data: JSON.stringify(param),
            headers: {
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

function UpNumComment() {
     var count = $(".comment_list").length
    $(".comment_count").html(count+"条评论")
    $(".detail_about .comment").html(count)
}