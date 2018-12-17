$(function () {
    // TODO 登录表单提交
    $(".login_form_con").submit(function (e) {
        e.preventDefault()
        var mobile = $(".login_form #mobile").val()
        var password = $(".login_form #password").val()

        if (!mobile) {
            $("#login-mobile-err").show();
            return;
        }

        if (!password) {
            $("#login-password-err").show();
            return;
        }

        // 发起登录请求
        param = {
            'mobile':mobile,
            'password':password,
        }
        $.ajax({
            url: "/passport/login",
            type:"post",
            data: JSON.stringify(param),
            contentType: "application/json",
            headers:{
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (response) {
                     if (response.errno == 0){
                    // 代表登录成功
                    location.reload()
                }
                else {
                    // 登录失败
                        alert(response.errmsg)
                }

            }
        })
    })


    // TODO 注册按钮点击
    $(".register_form_con").submit(function (e) {
        // 阻止默认提交操作
        e.preventDefault()

		// 取到用户输入的内容
        var mobile = $("#register_mobile").val()
        var smscode = $("#smscode").val()
        var password = $("#register_password").val()

		if (!mobile) {


            $("#register-mobile-err").show();
            return;
        }
        if (!smscode) {
            $("#register-sms-code-err").html("验证码不能为空");
            $("#register-sms-code-err").show();
            return;
        }
        if (!password) {
            $("#register-password-err").html("请填写密码!");
            $("#register-password-err").show();
            return;
        }

        // 对密码长度的判断
		if (password.length < 6) {
            $("#register-password-err").html("密码长度不能少于6位");
            $("#register-password-err").show();
            return;
        }

        // 发起注册请求
        param = {
		    'mobile': mobile,
            'smscode': smscode,
            'password': password
        }

        $.ajax({
            url: "/passport/register",

            type: "POST",
            // dataType: "json",
            contentType:'application/json',
            data:JSON.stringify(param),
            headers:{
              "X-CSRFToken": getCookie("csrf_token")
            },
            success:function (response) {
                if (response.errno == 0){
                    // 代表注册成功
                    location.reload()
                }
                else {
                    // 注册失败
                        alert(response.errmsg)
                }

            }
        })

    })
})


var imageCodeId = ""

// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 浏览器要发送的请求/image_code?imageCodeId
    imageCodeId = generateUUID()
    // 生成url
    var url = "/passport/image_code?imageCodeId="+ imageCodeId

    $(".get_pic_code").attr("src", url)

}

// 发送短信验证码
function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".get_code").removeAttr("onclick");
    var mobile = $("#register_mobile").val();
    if (!mobile) {
        $("#register-mobile-err").html("请填写正确的手机号！");
        $("#register-mobile-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#register-image-code-err").html("请填写验证码！");
        $("#register-image-code-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO 发送短信验证码
    // 初始化数据
    formData = {
        "mobile": mobile,
        "imageCode":imageCode,
        "image_code_id": imageCodeId
    }

    $.ajax({
        url: '/passport/sms_code',
        type: "post",
        // dataType: "json",
        data: JSON.stringify(formData),
        contentType:'application/json',
        headers:{
            "X-CSRFToken": getCookie("csrf_token")
        },
        success:function (response) {
            if (response.errno==0){
                // 发送成功显示出发送成功
                $("#register-sms-code-err").html("发送成功").show()
                // 设置倒计时
                num = 3
                $(".get_code").html(num)
                timmer = setInterval(function () {
                    num --
                    $(".get_code").html(num)
                    if (num<1){
                        // alert(num)
                        clearInterval(timmer)
                        $(".get_code").html("点击获取验证码")
                        $(".get_code").attr("onclick","sendSMSCode()");
                    }
                },1000)

            }else{
                alert(response.errmsg)

             $(".get_code").attr("onclick","sendSMSCode()");
            }

        }

    })


    // done(function (dat) {
    //     alert(dat.errmsg + "scuess")
    // }).fail(function (dat) {
    //     alert(dat.errmsg + "failed")
    // })

}

// 调用该函数模拟点击左侧按钮
function fnChangeMenu(n) {
    var $li = $('.option_list li');
    if (n >= 0) {
        $li.eq(n).addClass('active').siblings().removeClass('active');
        // 执行 a 标签的点击事件
        $li.eq(n).find('a')[0].click()
    }
}

// 一般页面的iframe的高度是660
// 新闻发布页面iframe的高度是900
function fnSetIframeHeight(num){
	var $frame = $('#main_frame');
	$frame.css({'height':num});
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function logout() {
    $.get("/passport/logout", function (resp) {
        location.reload()

    })
}
