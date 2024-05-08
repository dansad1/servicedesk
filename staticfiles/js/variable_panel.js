function insertVariable(variable) {
    if (CKEDITOR.instances.template_content) {
        CKEDITOR.instances.template_content.insertText('{{ ' + variable + ' }}');
    }
}

// Функция для фильтрации списка переменных по вводимому тексту
function filterVariables() {
    var input = document.getElementById("search-variable");
    var filter = input.value.toUpperCase();
    var panel = document.getElementById("variable-panel");
    var li = panel.getElementsByTagName("li");

    for (var i = 0; i < li.length; i++) {
        var txtValue = li[i].textContent || li[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}