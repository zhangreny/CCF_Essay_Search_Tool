// 论文按钮的相关操作
function essay_search() {

	//为防止过度点击，先锁住按钮
	document.getElementById('submit_search').onclick = null; // 解绑onclick事件
	console.log("提交搜索请求");

	var keywords_search = document.getElementById("keywords_search").value;
	
	if (keywords_search == "") {
		swal("Server Response", "填写搜索关键字呀", "error");
		return
	}
	
	var domain_select = document.getElementById("domain_select").value;
	var startyear_search = document.getElementById("startyear_search").value;
	var endyear_search = document.getElementById("endyear_search").value;
	var method_select = document.getElementById("method_select").value;
	
	if (domain_select == "--选择方向--") {
		swal("Server Response", "选择一个具体方向哦", "error");
		return
	}
	
	var startyearnum = parseInt(startyear_search);
	var endyearnum = parseInt(endyear_search);
	if (startyearnum > endyearnum) {
		swal("Server Response", "咋起始年份比终止年份还晚呢", "error");
		return
	}
	
	
	var formFile = new FormData();
	formFile.append("keywords_search", keywords_search);
	formFile.append("domain_select", domain_select);
	formFile.append("startyear_search", startyear_search);
	formFile.append("endyear_search", endyear_search);
	formFile.append("method_select", method_select);
	var data = formFile;
	$.ajax({
		url: "/api/search",
		data: data,
		type: "POST",
		dataType: "json",
		cache: false,
		processData: false,
		contentType: false,
		success: function (res) {
			if (res.status == "fail") {
				swal("Server Response", res.resultdata, "error");
			}
			else {
				const t = $("table#results_table tbody").empty();
				if (!res.resultdata || res.resultdata.length == 0) {
					swal("Server Response", "搜索成功！共找到"+res.resultdata.length+"篇论文", "success");
				}
				else {
					Array.from(res.resultdata).forEach(function (record, index) {
						$("<tr>").appendTo(t)
						$("<td style='padding-left:7px;padding-bottom:4px;'>"+record.JorC+"</td>").appendTo(t)
						$("<td style='padding-left:7px;padding-bottom:4px;'>"+record.year+"</td>").appendTo(t)
						$("<td style='padding-left:7px;padding-bottom:4px;'>"+record.name+"</td>").appendTo(t)
						$("</tr>").appendTo(t)
					});
					swal("Server Response", "搜索成功！共找到"+res.resultdata.length+"篇论文\n已按照年份排序", "success");
				}
			}
			// 把按钮解封
			document.getElementById('submit_search').onclick = function () {
              		essay_search();
              }
		},
	})
	
	

}
