// 用户注册按钮的相关操作
function user_register() {
	var username_register = document.getElementById("username_register").value;
	var passwd_register = document.getElementById("passwd_register").value;
	var confirmpasswd_register = document.getElementById("confirmpasswd_register").value;
	var nameorvxname_register = document.getElementById("nameorvxname_register").value;
	
	//为防止过度点击，先锁住按钮
	document.getElementById("submit_user_register").disabled = true;
	
	if (username_register == "" || passwd_register == "" || confirmpasswd_register == "" || nameorvxname_register == "") {
		swal("Server Response", "请补全字段", "error");
		return;
	}
	
	if (passwd_register != confirmpasswd_register) {
		swal("Server Response", "两次密码输入不一致", "error");
		return;
	}
	
	var formFile = new FormData();
	formFile.append("username_register", username_register);
	formFile.append("passwd_register", passwd_register);
	formFile.append("confirmpasswd_register", confirmpasswd_register);
	formFile.append("nameorvxname_register", nameorvxname_register);
	var data = formFile;
	$.ajax({
		url: "/api/register",
		data: data,
		type: "POST",
		dataType: "json",
		cache: false,
		processData: false,
		contentType: false,
		success: function (res) {
			if (res.status == "success") {
				document.getElementById("login").click();
				swal("Server Response", res.resultdata, "success");
			}
			else {
				swal("Server Response", res.resultdata, "error");
			}
		},
	})
	// 把按钮解封
	document.getElementById("submit_user_register").disabled = false;
}

//用户登录按钮的操作
function user_login() {
	var username_login = document.getElementById("username_login").value;
	var passwd_login = document.getElementById("passwd_login").value;
	
	//为防止过度点击，先锁住按钮
	document.getElementById("submit_user_login").disabled = true;
	
	if (username_login == "" || passwd_login == "") {
		swal("Server Response", "请补全字段", "error");
		return;
	}
	
	var formFile = new FormData();
	formFile.append("username_login", username_login);
	formFile.append("passwd_login", passwd_login);
	var data = formFile;
	$.ajax({
		url: "/api/login",
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
				window.location.href = "search";
			}
		},
	})
	// 把按钮解封
	document.getElementById("submit_user_login").disabled = false;
}