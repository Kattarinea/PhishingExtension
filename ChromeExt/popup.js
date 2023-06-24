document.addEventListener('DOMContentLoaded', function() {
  var scanButton = document.getElementById('scanButton');
  var image = document.getElementById('img');

  if (scanButton) {
    scanButton.addEventListener('click', function() {
      chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        var url = tabs[0].url;
        var xhr = new XMLHttpRequest();
	
		xhr.open("POST", "http://127.0.0.1:8000");
		xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
		xhr.send(JSON.stringify({url: url}));

		

        xhr.onload = function() {
          if (xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);
			var switchBtn = document.getElementById('switchBtn');
            if (response.status == 1 && switchBtn.checked==false) {
              image.src = '/icons/Phish128.png';
            } else if (response.status == 0 && switchBtn.checked==false) {
              image.src = '/icons/Benign128.png';
            }
            document.body.appendChild(image);
          } else {
            console.log('Request failed.  Returned status of ' + xhr.status);
          }
		  
        };
      });
    });
  }
});

// Загрузка сохраненного значения из хранилища
  chrome.storage.sync.get('switchState', function(data) {
    switchBtn.checked = data.switchState;
	if (switchBtn.checked) {
      scanButton.style.backgroundColor = "#ccc";
      scanButton.style.border = "2px solid #ccc"; 
    } else {
      scanButton.style.backgroundColor = "#ff4500";
      scanButton.style.border = "2px solid #E60000"; 
    }
    scanButton.disabled = data.switchState;

   
});

switchBtn.addEventListener('click', function() {
    scanButton.disabled = this.checked;
    if (this.checked) {
      scanButton.style.backgroundColor = "#ccc";
      scanButton.style.border = "2px solid #ccc"; 
	  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            chrome.tabs.reload(tabs[0].id);
        });
	 
    } else {
      scanButton.style.backgroundColor = "#ff4500";
      scanButton.style.border = "2px solid #E60000"; 
    }

    // Сохранение значения в хранилище
    chrome.storage.sync.set({ 'switchState': this.checked });
	});
	