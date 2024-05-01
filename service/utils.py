import json

def serialize_data(data):
    """Сериализация данных в JSON строку."""
    return json.dumps(data)

def deserialize_data(data):
    """Десериализация JSON строки в данные."""
    return json.loads(data) if data else None