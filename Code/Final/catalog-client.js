catalog client script b4 workflow

// long and short project name
function onSubmit() {
	var f1=g_form.getValue("projectname_short");
	if (f1.length > 10) {
		alert('Length of Short Project Name is More than 10 characters');
		return false;
	}
	var f2=g_form.getValue("projectname_short");
	if (f2.length > 10) {
		alert('Length of Short Project Name is More than 30 characters');
		return false;
	}


	var usernames = ${current.variables.users}.toString(); //correct syntax?
	gs.log("Nich: content of usernames:" + usernames);

	function parser(string) {
	    var text = string;
	    text = text.replace(/\s+/g, '');
	    text = text.split(',');
	    return text;
	}

	var list_usernames = parser(usernames);
	workflow.scratchpad.users = list_usernames;

