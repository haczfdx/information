// 解析url中的查询字符串
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(function(){
    // 页面加载完毕，获取新闻列表
    getNewsList(1)

    // 关注当前新闻作者
    $(".focus").click(function () {

        var user_id = $(this).attr("user_id")
        // alert(news_user_id)
        var params = {
            'user_id': user_id,
            'action': "follow"
        }
        $.ajax({
            url: "/news/follower_user",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),

            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (response) {
                if(response.errno==0){
                     $(".focus").hide()
                    $(".focused").show()
                     $(".follows b").html(Number($(".follows b").html())+1)

                }else {
                    alert(response.errmsg)
                }


            }

        })
    })

    // 取消关注当前新闻作者
    $(".focused").click(function () {
 var user_id = $(this).attr("user_id")
        // alert(news_user_id)
        var params = {
            'user_id': user_id,
            'action': "unfollow"
        }
        $.ajax({
            url: "/news/follower_user",
            type: "post",
            data: JSON.stringify(params),
            contentType: "application/json",
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (response) {
                if(response.errno==0){
                     $(".focused").hide()
                     $(".focus").show()
                         $(".follows b").html(Number($(".follows b").html())-1)


                }else {
                    alert(response.errmsg)
                }


            }

        })
    })
})

// 获取新闻列表
function getNewsList(page) {
    var query = decodeQuery()
    var params = {
        "p": page,
        "user_id": query["user_id"]
    }
    $.get("/user/other_news_list", params, function (resp) {
        if (resp.errno == "0") {
            // 先清空原有的数据
            $(".article_list").html("");
            // 拼接数据
            for (var i = 0; i<resp.data.news_list.length; i++) {
                var news = resp.data.news_list[i];
                var html = '<li><a href="/news/'+ news.id +'" target="_blank">' + news.title + '</a><span>' + news.create_time + '</span></li>'
                // 添加数据
                $(".article_list").append(html)
            }
            // 设置页数和总页数
            $("#pagination").pagination("setPage", resp.data.current_page, resp.data.total_page);
        }else {
            alert(resp.errmsg)
        }
    })
}
