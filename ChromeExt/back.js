document.addEventListener('DOMContentLoaded', function() {
  window.back = 0;//инициализация глобальной переменной
});

var backButton = document.getElementById('backButton');
backButton.addEventListener('click', function() {//отслеживание нажатия кнопки
  window.back=1;
  navigator.serviceWorker.controller.postMessage({ type: 'back', value: window.back });//отправка сообщения на serviceWorker с переменной back
  window.history.back();//переход на предыдущую страницу браузера
});