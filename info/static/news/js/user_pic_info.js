function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function (e) {
        e.preventDefault()

        // 上传头像
        $(this).ajaxSubmit({
            url: "/user/user_pic_info",
            type: "POST",
             headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (response) {
                if (response.errno == 0){
                    // 成功
                    $(".now_user_pic").attr("src", response.data.avatar_url)
                    $(".user_login img", parent.document).attr("src", response.data.avatar_url)
                    $(".user_center_pic img", parent.document).attr("src", response.data.avatar_url)
                }else {
                    // 失败
                    alert("上传失败")
                }
            }
        })
    })
})