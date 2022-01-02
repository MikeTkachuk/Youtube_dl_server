function log_message(msg){
	document.getElementById("log").innerHTML += `${msg}<br>`;
};

function clear_log(){
	document.getElementById("log").innerHTML = '';
};

function init_test(){
	var url_val = document.getElementById('url').value; 
	var params = new URLSearchParams({'url':url_val});
	var req = new XMLHttpRequest();
	req.open('get',`/get_url?${params.toString()}`);
	req.onload = () => {
		log_message(`Received link:/get_data/${req.responseText}`);
		const anch = document.createElement('a');
		anch.href = `/get_data/${req.responseText}`;
		document.body.appendChild(anch);
		anch.click();
		document.body.removeChild(anch);
	}
	req.send()

	log_message('Downloading media...');
};