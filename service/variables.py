
AVAILABLE_VARIABLES = {
    'Request': {
        'title': 'Заголовок заявки',
        'description': 'Описание заявки',
        'requester_username': 'Имя пользователя, создавшего заявку',
        'assignee_username': 'Имя пользователя, назначенного на заявку',
        'company_name': 'Название компании',
        'status_name': 'Текущий статус заявки',
        'created_at': 'Дата и время создания заявки',
        'updated_at': 'Дата и время последнего обновления',
        'priority_name': 'Приоритет заявки',
        'request_type_name': 'Тип заявки',
        'due_date': 'Срок выполнения заявки',
        'attachment_url': 'Ссылка на прикрепленный файл',
    },
    'Comment': {
        'text': 'Текст комментария',
        'author_username': 'Имя автора комментария',
        'created_at': 'Дата и время создания комментария',
        'attachment_url': 'Ссылка на прикрепленный файл комментария',
        'content': 'Содержание комментария',
    }
}
EVENT_CHOICES = [
    ('create_request', 'Создание заявки'),
    ('update_request', 'Изменение полей заявки'),
    ('add_comment', 'Добавление комментария'),
    ('deadline_expiration', 'Истечение срока заявки'),
    ('status_change', 'Смена статуса заявки'),
]