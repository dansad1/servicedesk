import json
from django.utils import timezone
from service.models import PriorityDuration, FieldMetadata, RequestFiledValue, Status

def serialize_data(data):
    """Сериализация данных в JSON строку."""
    return json.dumps(data)

def deserialize_data(data):
    """Десериализация JSON строки в данные."""
    return json.loads(data) if data else None

