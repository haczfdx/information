function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
 // 取消关注当前新闻作者
    $(".focused").click(function () {
 var user_id = $(this).attr("user_id")
        var $this = $(this)
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
                     $this.parent().hide()

                         $(".follows b").html(Number($(".follows b").html())-1)


                }else {
                    alert(response.errmsg)
                }


            }

        })
    })
})