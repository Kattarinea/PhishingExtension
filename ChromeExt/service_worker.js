var k = 'no';

self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'back') {
    k = 'back_safe'; //обновляем значение переменной k при получении сообщения 'back'
  }
});

function handleUpdated(tabId, changeInfo, tab) {
  if (tab && tab.url) {
    if (changeInfo.status == 'loading') { //состояние вкладки изменилось на 'loading'
      chrome.storage.sync.get('switchState', function(data) { //получаем состояние switch из хранилища
        if (data.switchState && k !== 'back_safe') {
          var url_ = tab.url;
          if (url_.search('chrome-extension://') < 0 && url_.search('chrome://') < 0) {
            fetch('http://127.0.0.1:8000', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json;charset=UTF-8'
              },
              body: JSON.stringify({ url: url_ })//отправляем запрос на сервер
            }).then(function(response) {
              if (response.ok) {
                return response.json();
              } 
            }).then(function(json) {
              if (json.status == 1 && data.switchState == true) { //обрабаытваем полученный от сервера ответ, меняя иконку
                chrome.action.setIcon({ path: '/icons/Phish128.png', tabId: tabId });
                chrome.tabs.update(tabId, { url: "error_page.html" });
              } else if (json.status == 0 && data.switchState == true) {
                chrome.action.setIcon({ path: '/icons/Benign128.png', tabId: tabId });
              }
            }).catch(function(error) {
              console.log('Fetch error:', error);
            });
          }
        } else if (k == 'back_safe') {
          k = 'no';
        }
      });
    }
  }
}

chrome.tabs.onCreated.addListener(handleUpdated); //слушатель события создания вкладки
chrome.tabs.onUpdated.addListener(handleUpdated); //слушатель события обновления вкладки
