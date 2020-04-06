function addRule() {

	/* Get resources */
	var leftElement = document.getElementById("userList1");
	var matchElement = document.getElementById("matchType");
	var rightElement = document.getElementById("userList2");
	var leftName = leftElement.options[leftElement.selectedIndex].text;
	var matchName = matchElement.options[matchElement.selectedIndex].text;
	var rightName = rightElement.options[rightElement.selectedIndex].text;
	var list = document.getElementById("ruleList");

	/* Create rule */
	var rule = {};
	rule['left'] = parseInt(leftElement.options[leftElement.selectedIndex].value);
	rule['match'] = parseInt(matchElement.options[matchElement.selectedIndex].value);
	rule['right'] = parseInt(rightElement.options[rightElement.selectedIndex].value);

	/* Build list element */
	var div = document.createElement("div");
	list.appendChild(div);
	div.className = "rule";
	var hidden = document.createElement("input");
	div.appendChild(hidden);
	hidden.type = "hidden";
	hidden.name = "rules[]";
	hidden.value = JSON.stringify(rule);
	var para = document.createElement("p");
	div.appendChild(para);
	var text = document.createTextNode(leftName + " " + matchName + " " + rightName);
	para.appendChild(text)
	var link = document.createElement("a");
	div.appendChild(link);
	link.href = "javascript:void(0)";
	link.className = "warning";
	link.onclick = function() { this.parentNode.remove(); };
	var icon = document.createElement("i");
	link.appendChild(icon);
	icon.className = "fas fa-times-circle";
}
