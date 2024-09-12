// script.js  
document.addEventListener('DOMContentLoaded', function() {  
    // 获取所有具有'add-text'类的链接  
    var links = document.querySelectorAll('.add-text');  
  
    // 为每个链接添加点击事件监听器  
    links.forEach(function(link) {  
        link.addEventListener('click', function(event) {  
            // 阻止链接的默认行为  
            event.preventDefault();  
  
            // 获取textarea元素  
            var textarea = document.getElementById('myTextarea');  
  
            // 从链接的data-text属性中获取文本  
            var textToAdd = this.getAttribute('data-text');  

            // 将文本添加到textarea
            textarea.value = textToAdd + '\r' + '\n';  
        });  
    });  
});