CKEDITOR.editorConfig = function( config ) {
    // Отключаем стандартные плагины WYSIWYG, оставляя только редактор исходного кода
    config.removePlugins = 'about,clipboard,find,forms,link,liststyle,preview,tabletools,scayt,menubutton,contextmenu';
    config.allowedContent = true; // Разрешаем все содержимое HTML без фильтрации
    config.extraPlugins = 'sourcedialog'; // Подключаем плагин редактирования исходного кода
    config.removeButtons = 'Save,NewPage'; // Убираем ненужные кнопки
};
