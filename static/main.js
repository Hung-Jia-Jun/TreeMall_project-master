
function getTextValue() {
	userTypeUrl = (document.getElementById("url").value);
	
	$.get("/UserShortUrl",
		{url : userTypeUrl},
		function(data) {
			console.log(data);
			document.getElementById("response").innerText = data
		}
	);
}
$(document).ready(function(){
	document.getElementById("confirm").addEventListener("click", getTextValue);
});