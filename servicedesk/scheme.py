from graphviz import Digraph

# Инициализация Digraph для создания блок-схемы
dot = Digraph(comment='Детализированная блок-схема сервис-деска')

# Добавление узлов
dot.node('A', 'Начало')
dot.node('B', 'Аутентификация пользователя')
dot.node('C', 'Успешная аутентификация?')
dot.node('D', 'Определение роли')
dot.node('E', 'Главное меню')
dot.node('F1', 'Функции Клиента')
dot.node('F2', 'Функции Оператора')
dot.node('F3', 'Функции Администратора')
dot.node('G', 'Выполнение выбранного действия')
dot.node('H', 'Продолжить работу?')
dot.node('I', 'Выход')
dot.node('X', 'Неудачная аутентификация', shape='diamond')

# Добавление связей между узлами
dot.edge('A', 'B')
dot.edge('B', 'C', label='Проверка данных')
dot.edge('C', 'D', label='Да')
dot.edge('C', 'X', label='Нет')
dot.edge('X', 'B', label='Возврат к аутентификации')
dot.edge('D', 'E')
dot.edge('E', 'F1', label='Клиент')
dot.edge('E', 'F2', label='Оператор')
dot.edge('E', 'F3', label='Администратор')
dot.edge('F1', 'G')
dot.edge('F2', 'G')
dot.edge('F3', 'G')
dot.edge('G', 'H')
dot.edge('H', 'E', label='Да')
dot.edge('H', 'I', label='Нет')

# Визуализация блок-схемы
print(dot.source)  # Вывод кода блок-схемы
dot.render('service_desk_detailed_scheme', view=True)  # Сохранение и отображение блок-схемы