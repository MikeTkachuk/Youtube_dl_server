function log_message(msg){
	document.getElementById("log").innerHTML += `${msg}<br>`;
};

function clear_log(){
	document.getElementById("log").innerHTML = '';
};

function make_order(){
	var url_val = document.getElementById('url').value; 
	var params = new URLSearchParams({'url':url_val});
	var req = new XMLHttpRequest();
	req.open('get',`/get_receipt?${params.toString()}`);
	req.onload = async () => {
		if (req.status != 200){
			log_message(req.responseText);
			return;
		}
		var receipt = req.responseText;
		log_message(`Downloading ${receipt}...`);
		
		var url_ready = false;
		var file_url;
		while (!url_ready){
			var url_params = new URLSearchParams({'receipt':receipt});
			var url_req = new XMLHttpRequest();
			url_req.open('get',`/get_url?${url_params.toString()}`);
			
			url_req.onload = async () => {
				if(url_req.responseText!=""){
					file_url = url_req.responseText;
					url_ready = true;
				};
			};			

			url_req.send();
			await new Promise(r => setTimeout(r, 1000));
		}
		download_from_link(`/get_data/${file_url}`);
	};
	req.send()

};

function download_from_link(link){
	const anch = document.createElement('a');
	anch.href = link;
	document.body.appendChild(anch);
	anch.click();
	document.body.removeChild(anch);
	log_message(`Successfully downloaded.<br>`);
};