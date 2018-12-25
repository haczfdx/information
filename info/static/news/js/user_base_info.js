function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault();

        var signature = $("#signature").val()
        var nick_name = $("#nick_name").val()
        var gender = $("input:radio:checked").val()
        // alert(gender)

        if (!nick_name) {
            alert('请输入昵称')
            return
        }
        if (!gender) {
            alert('请选择性别')
        }

        //  修改用户信息接口
          var param = {
            "signature":signature,
              "nick_name":nick_name,
              "gender": gender
          }
          $.ajax({
              url: "",
              type: "POST",
              contentType: "application/json",
              headers:{"X-CSRFToken": getCookie("csrf_token")},
              data: JSON.stringify(param),
              success: function (response) {
                  if(response.errno==0){
                      // 成功
                      // $(".user_center_name").html(nick_name)
                      // $("#nick_name").html(nick_name)
                      //
                      // location.reload()
                    $('.user_center_name', parent.document).html(param['nick_name'])
                    $('#nick_name', parent.document).html(param['nick_name'])
                    $('.input_sub').blur()
                  }else if (response.errno == 4102) {
                       parent.location.reload()
                      // alert("12313")
                      // $('.login_form_con', parent.document).show()
                  }else {
                       alert("12313")
                      // 失败
                      alert(response.errmsg)
                  }

              }
          })

    })
})