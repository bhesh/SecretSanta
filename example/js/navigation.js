function navExpand() {
	var x = document.getElementById("navLinks");
	if (x.style.display === "block") {
		x.style.display = "none";
	} else {
		x.style.display = "block";
	}
}
function groupExpand() {
	var x = document.getElementById("groupMenu");
	if (x.style.display === "block") {
		x.style.display = "none";
	} else {
		x.style.display = "block";
	}
}
function navShow() {
	var x1 = document.getElementById("navLinks");
	var x2 = document.getElementById("desktopNavLinks");
	var x3 = document.getElementById("groupMenu");
	if (window.outerWidth > 768) {
		x1.style.display = "none";
		x2.style.display = "inline";
		x3.style.display = "block";
	} else {
		x1.style.display = "none";
		x2.style.display = "none";
		x3.style.display = "none";
	}
}
