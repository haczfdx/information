function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();
        var old_pwd = $("#old_pwd").val()
        var new_pwd1 = $("#new_pwd1").val()
        var new_pwd2 = $("#new_pwd2").val()

        var param = {
            "old_pwd": old_pwd,
            "new_pwd1": new_pwd1,
            "new_pwd2": new_pwd2
        }
        $.ajax({
            url: "",
            type: "POST",
            contentType: "application/json",
            headers: {"X-CSRFToken": getCookie("csrf_token")},
            data: JSON.stringify(param),
            success: function (response) {
                if (response.errno == 0) {
                    // 成功
                    alert("修改成功")
                    $.get("/passport/logout")
                } else if (response.errno == 4102) {
                    $('.login_form_con').show()
                } else {
                    // 失败
                    alert(response.errmsg)
                }

            }
        })
    })
})