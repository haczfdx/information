var currentCid = 0; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid')
        $('.menu li').each(function () {
            $(this).removeClass('active')
        })
        $(this).addClass('active')

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = Number(clickCid)

            // 重置分页参数
            cur_page = 1
            total_page = 1
            updateNewsData()
        }
    })

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
        }
    })
})

function updateNewsData() {
    // TODO 更新新闻数据
    // alert(currentCid)
    var index_content = $(".conter_con .list_con")
    var content_str = ""
    $.ajax({
        url: "/news/list",
        type: "get",
        data:{"class_cid": currentCid},
        success: function (response) {
            content_data = response.errmsg
            for (var i=0; i<content_data.length;i++){
            // console.log(content_data[i].index_image_url)
            content_str+='<li>'+
                '<a href="#" class="news_pic fl"><img src="'+content_data[i].index_image_url+'"></a>'+
                '<a href="#" class="news_title fl">'+content_data[i].title+'</a>'+
                '<a href="#" class="news_detail fl">'+content_data[i].digest+'</a>'+
                '<div class="author_info fl">'+
                    '<div class="author fl">'+
                        '<img src="../../static/news/images/person.png" alt="author">'+
                        '<a href="#">'+content_data[i].source+'</a>'+
                    '</div>'+
                    '<div class="time fl">'+content_data[i].create_time+'</div>'+
                '</div>'+
            '</li>'
            }
            index_content.html(content_str)
            console.log(content_data)

        }

    })

}
