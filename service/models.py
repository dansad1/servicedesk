from absl.flags import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from ckeditor.fields import RichTextField  # Import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker
from servicedesk import settings


class Company(models.Model):
    # Общие данные
    name = models.CharField(_("Название компании"), max_length=255, unique=True)
    region = models.CharField(_("Регион"), max_length=255, default="Не указан")

    # Контактные данные
    address = models.CharField(_("Адрес"), max_length=1024, blank=True)
    phone = models.CharField(_("Телефон"), max_length=20, blank=True)
    email = models.EmailField(_("Электронная почта"), blank=True)
    website = models.URLField(_("Веб-сайт"), blank=True)

    # Дополнительные данные
    description = models.TextField(_("Описание"), blank=True)

    # Новые поля
    ceo = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='company_ceo',
                            on_delete=models.SET_NULL, null=True, blank=True,
                            verbose_name=_("Генеральный директор"))
    deputy = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='company_deputy',
                               on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name=_("Заместитель генерального директора"))
    contact_person = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='company_contact_person',
                                       on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name=_("Контактное лицо"))
    timezone = models.CharField(_("Часовой пояс"), max_length=50, default='UTC')

    class Meta:
        verbose_name = _("компания")
        verbose_name_plural = _("компании")

    def __str__(self):
        return self.name
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Компания')
    department = models.ForeignKey('Department', null=True, blank=True, on_delete=models.SET_NULL)
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.username
class Department(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    parent = models.ForeignKey('self', related_name='subdepartments', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Родительское подразделение")
    company = models.ForeignKey('Company', related_name='departments', on_delete=models.CASCADE, verbose_name="Компания")
    users = models.ManyToManyField(CustomUser, related_name='departments', blank=True, verbose_name="Сотрудники")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"


class CustomPermission(models.Model):
    code_name = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class GroupPermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    custompermission = models.ForeignKey(CustomPermission, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=20,
        choices=[
        ('personal', 'Personal'),
        ('department', 'Department'),
        ('global', 'Global')
    ],
    default='personal')
class Status(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
class Priority(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name
class FieldMeta(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('textarea', 'Textarea'),
        ('select', 'Select'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('boolean', 'Boolean'),
        ('email', 'Email'),
        ('url', 'URL'),
        ('json', 'JSON'),
        ('status', 'Status'),
        ('company', 'Company'),
        ('priority', 'Priority'),
        ('requester', 'Requester'),
        ('assignee', 'Assignee'),
        ('request_type', 'Request Type'),
        ('file', 'File'),
        ('comment', 'Comment'),

    ]

    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=False)
    show_name = models.BooleanField(default=True)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    hint = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
def get_default_value(self):
        if self.field_type == 'status' and self.default_value:
            try:
                return Status.objects.get(id=self.default_value)
            except Status.DoesNotExist:
                return None
        # Другие типы полей могут быть добавлены аналогично
        return self.default_value

class FieldSet(models.Model):
    name = models.CharField(max_length=100)
    fields = models.ManyToManyField(FieldMeta, blank=True, related_name='field_sets')

    def __str__(self):
        return self.name

    def add_default_fields(self):
        default_fields = [
            {"name": "Title", "field_type": "text", "is_required": True, "show_name": True, "default_value": "", "unit": "", "hint": ""},
            {"name": "Description", "field_type": "textarea", "is_required": True, "show_name": True, "default_value": "", "unit": "", "hint": ""},
            {"name": "Due Date", "field_type": "date", "is_required": False, "show_name": True, "default_value": "", "unit": "", "hint": ""},
            {"name": "Attachment", "field_type": "file", "is_required": False, "show_name": True, "default_value": "", "unit": "", "hint": ""},
            {"name": "Requester", "field_type": "requester", "is_required": True, "show_name": True, "default_value": "", "unit": "", "hint": ""},
            {"name": "Assignee", "field_type": "assignee", "is_required": False, "show_name": True, "default_value": "", "unit": "", "hint": ""},
            {"name": "Company", "field_type": "company", "is_required": True, "show_name": True, "default_value": "", "unit": "", "hint": ""},
            {"name": "Status", "field_type": "status", "is_required": True, "show_name": True, "default_value": "", "unit": "", "hint": ""},
            {"name": "Priority", "field_type": "priority", "is_required": False, "show_name": True, "default_value": "", "unit": "", "hint": ""},
            {"name": "Comments", "field_type": "comment", "is_required": False, "show_name": True, "default_value": "",
             "unit": "", "hint": ""},

        ]
        for field in default_fields:
            field_meta, created = FieldMeta.objects.get_or_create(
                name=field["name"],
                field_type=field["field_type"],
                defaults={
                    "is_required": field["is_required"],
                    "show_name": field["show_name"],
                    "default_value": field["default_value"],
                    "unit": field["unit"],
                    "hint": field["hint"]
                }
            )
            self.fields.add(field_meta)


class RequestType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    field_set = models.ForeignKey(FieldSet, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.field_set:
            default_field_set = FieldSet.objects.create(name=f"Default for {self.name}")
            default_field_set.add_default_fields()
            self.field_set = default_field_set
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class PriorityDuration(models.Model):
    request_type = models.ForeignKey(RequestType, on_delete=models.CASCADE)
    priority = models.ForeignKey(Priority, on_delete=models.CASCADE)
    duration_in_hours = models.IntegerField(default=0)

    class Meta:
        unique_together = ('priority', 'request_type')

    def __str__(self):
        return f"{self.priority.name} for {self.request_type.name} : {self.duration_in_hours} hours"

class FieldAccess(models.Model):
    role = models.ForeignKey(Group, on_delete=models.CASCADE)
    field_meta = models.ForeignKey('FieldMeta', on_delete=models.CASCADE)
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)

class FieldValue(models.Model):
    field_meta = models.ForeignKey(FieldMeta, on_delete=models.CASCADE)
    request = models.ForeignKey('Request', on_delete=models.CASCADE, related_name='field_values')
    value_text = models.TextField(blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    value_email = models.EmailField(null=True, blank=True)
    value_url = models.URLField(null=True, blank=True)
    value_json = models.JSONField(null=True, blank=True)
    value_status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True, blank=True)
    value_company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True)
    value_priority = models.ForeignKey('Priority', on_delete=models.SET_NULL, null=True, blank=True)
    value_requester = models.ForeignKey(CustomUser, related_name='value_requester', on_delete=models.SET_NULL, null=True, blank=True)
    value_assignee = models.ForeignKey(CustomUser, related_name='value_assignee', on_delete=models.SET_NULL, null=True, blank=True)
    value_request_type = models.ForeignKey('RequestType', on_delete=models.SET_NULL, null=True, blank=True)
    value_file = models.FileField(upload_to='field_files/', null=True, blank=True)

    def __str__(self):
        return f"{self.field_meta.name}: {self.get_value()}"

    def get_value(self):
        type_map = {
            'text': self.value_text,
            'textarea': self.value_text,
            'number': self.value_number,
            'date': self.value_date,
            'boolean': self.value_boolean,
            'email': self.value_email,
            'url': self.value_url,
            'json': self.value_json,
            'status': self.value_status.id if self.value_status else None,
            'company': self.value_company.id if self.value_company else None,
            'priority': self.value_priority.id if self.value_priority else None,
            'requester': self.value_requester.id if self.value_requester else None,
            'assignee': self.value_assignee.id if self.value_assignee else None,
            'request_type': self.value_request_type.id if self.value_request_type else None,
            'file': self.value_file.name if self.value_file else None,
        }
        return type_map.get(self.field_meta.field_type)

    def set_value(self, value):
        if self.field_meta.field_type == 'status':
            self.value_status_id = value if value else None
        elif self.field_meta.field_type == 'company':
            self.value_company_id = value if value else None
        elif self.field_meta.field_type == 'priority':
            self.value_priority_id = value if value else None
        elif self.field_meta.field_type == 'requester':
            self.value_requester_id = value if value else None
        elif self.field_meta.field_type == 'assignee':
            self.value_assignee_id = value if value else None
        elif self.field_meta.field_type == 'request_type':
            self.value_request_type_id = value if value else None
        elif self.field_meta.field_type == 'file':
            self.value_file = value
        else:
            field_name = {
                'text': 'value_text',
                'textarea': 'value_text',
                'number': 'value_number',
                'date': 'value_date',
                'boolean': 'value_boolean',
                'email': 'value_email',
                'url': 'value_url',
                'json': 'value_json',
            }.get(self.field_meta.field_type)
            if field_name:
                setattr(self, field_name, value)
class Request(models.Model):
    request_type = models.ForeignKey(RequestType, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.id}"

    def set_default_values(self, user):
        if not self.request_type:
            raise ValueError("Request type must be set before setting default values.")

        default_fields = self.request_type.field_set.fields.all()
        for field_meta in default_fields:
            if not FieldValue.objects.filter(request=self, field_meta=field_meta).exists():
                default_value = self.get_default_value(field_meta, user)
                FieldValue.objects.create(
                    request=self,
                    field_meta=field_meta,
                    **default_value
                )

    def get_default_value(self, field_meta, user):
        try:
            if field_meta.field_type == 'status' and field_meta.default_value:
                return {'value_status': Status.objects.get(id=field_meta.default_value)}
            elif field_meta.field_type == 'company' and field_meta.default_value:
                return {'value_company': Company.objects.get(id=field_meta.default_value)}
            elif field_meta.field_type == 'priority' and field_meta.default_value:
                return {'value_priority': Priority.objects.get(id=field_meta.default_value)}
            elif field_meta.field_type == 'requester':
                return {'value_requester': user}
            elif field_meta.field_type == 'assignee':
                return {'value_assignee': None}
            else:
                return {
                    'text': {'value_text': field_meta.default_value},
                    'textarea': {'value_text': field_meta.default_value},
                    'number': {'value_number': float(field_meta.default_value) if field_meta.default_value else 0},
                    'date': {'value_date': field_meta.default_value if field_meta.default_value else timezone.now().date()},
                    'boolean': {'value_boolean': field_meta.default_value.lower() == 'true' if field_meta.default_value else False},
                    'email': {'value_email': field_meta.default_value},
                    'url': {'value_url': field_meta.default_value},
                    'json': {'value_json': field_meta.default_value},
                    'file': {'value_file': field_meta.default_value},
                }.get(field_meta.field_type, {})
        except (Status.DoesNotExist, Company.DoesNotExist, Priority.DoesNotExist, CustomUser.DoesNotExist):
            return {}

    def get_field_values(self):
        values = {}
        for field_value in self.field_values.all():
            field_type = field_value.field_meta.field_type
            if field_type == 'text' or field_type == 'textarea':
                values[field_value.field_meta.name] = field_value.value_text
            elif field_type == 'number':
                values[field_value.field_meta.name] = field_value.value_number
            elif field_type == 'date':
                values[field_value.field_meta.name] = field_value.value_date
            elif field_type == 'boolean':
                values[field_value.field_meta.name] = field_value.value_boolean
            elif field_type == 'email':
                values[field_value.field_meta.name] = field_value.value_email
            elif field_type == 'url':
                values[field_value.field_meta.name] = field_value.value_url
            elif field_type == 'json':
                values[field_value.field_meta.name] = field_value.value_json
            elif field_type == 'status':
                values[
                    field_value.field_meta.name] = field_value.value_status.name if field_value.value_status else None
            elif field_type == 'company':
                values[
                    field_value.field_meta.name] = field_value.value_company.name if field_value.value_company else None
            elif field_type == 'priority':
                values[
                    field_value.field_meta.name] = field_value.value_priority.name if field_value.value_priority else None
            elif field_type == 'requester' or field_type == 'assignee':
                user = field_value.value_requester if field_type == 'requester' else field_value.value_assignee
                values[field_value.field_meta.name] = user.username if user else None
            elif field_type == 'request_type':
                values[
                    field_value.field_meta.name] = field_value.value_request_type.name if field_value.value_request_type else None
            elif field_type == 'file':
                values[field_value.field_meta.name] = field_value.value_file.url if field_value.value_file else None
        return values

class Comment(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = RichTextUploadingField()
    attachment = models.FileField(upload_to='comments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class StatusTransition(models.Model):
    from_status = models.ForeignKey(Status, related_name='from_transitions', on_delete=models.CASCADE)
    to_status = models.ForeignKey(Status, related_name='to_transitions', on_delete=models.CASCADE)
    allowed_groups = models.ManyToManyField(Group)

    class Meta:
        unique_together = ('from_status', 'to_status')

    def __str__(self):
        return f"{self.from_status.name} -> {self.to_status.name}"
class SavedFilter(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    filter_name = models.CharField(max_length=100)
    # Добавьте поля для сохранения фильтров, например, JSON-поле для данных фильтра
    filter_data = models.JSONField()

    def __str__(self):
        return self.filter_name


class EmailSettings(models.Model):
    CONNECTION_TYPE_CHOICES = [
        ('tls', 'TLS'),
        ('ssl', 'SSL'),
    ]

    server = models.CharField(max_length=255)
    port = models.IntegerField()
    login = models.EmailField()
    password = models.CharField(max_length=255)
    email_from = models.EmailField()
    connection_type = models.CharField(
        max_length=3,
        choices=CONNECTION_TYPE_CHOICES,
        default='tls',
    )

    def __str__(self):
        return self.server

    @property
    def use_tls(self):
        return self.connection_type == 'tls'

    @property
    def use_ssl(self):
        return self.connection_type == 'ssl'

EVENT_CHOICES = [
    ('create_request', 'Создание заявки'),
    ('update_request', 'Изменение полей заявки'),
    ('add_comment', 'Добавление комментария'),
    ('deadline_expiration', 'Истечение срока заявки'),
]
class NotificationTemplate(models.Model):
    type = models.CharField(max_length=100, choices=[('email', 'Email'), ('sms', 'SMS'), ('push', 'Push Notification')])
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    body = RichTextUploadingField(help_text="Используйте инструменты редактора для форматирования текста.")

    def __str__(self):
        return self.name

class NotificationSetting(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    event = models.CharField(max_length=50, choices=EVENT_CHOICES)
    email_template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name='email_settings')
    sms_template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name='sms_settings')
    push_template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name='push_settings')
    telegram_template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name='telegram_settings')
    whatsapp_template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name='whatsapp_settings')

    def __str__(self):
        return f'{self.group.name} - {self.get_event_display()}'

    def get_event_display(self):
        event_dict = dict(EVENT_CHOICES)
        return event_dict.get(self.event, self.event)
class PerformerGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(CustomUser, related_name='performer_groups')
    companies = models.ManyToManyField(Company, related_name='service_groups')

    def __str__(self):
        return self.name

class AssetType(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name

class Attribute(models.Model):
    TEXT = 'text'
    NUMBER = 'number'
    DATE = 'date'
    BOOLEAN = 'boolean'
    EMAIL = 'email'
    URL = 'url'
    JSON = 'json'
    ASSET_REFERENCE = 'asset_ref'
    ATTRIBUTE_REFERENCE = 'attr_ref'

    ATTRIBUTE_TYPES = [
        (TEXT, 'Текст'),
        (NUMBER, 'Число'),
        (DATE, 'Дата'),
        (BOOLEAN, 'Логический'),
        (EMAIL, 'Электронная почта'),
        (URL, 'Ссылка'),
        (JSON, 'JSON'),
        (ASSET_REFERENCE, 'Ссылка на актив'),
        (ATTRIBUTE_REFERENCE, 'Ссылка на атрибут'),
    ]

    name = models.CharField(max_length=255)
    attribute_type = models.CharField(max_length=50, choices=ATTRIBUTE_TYPES)

    def __str__(self):
        return f"{self.name} ({self.get_attribute_type_display()})"

class Asset(models.Model):
    name = models.CharField(max_length=255)
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE, related_name='assets')
    parent_asset = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='components')

    def __str__(self):
        return self.name

class AssetTypeAttribute(models.Model):
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE, related_name='type_attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.asset_type.name} - {self.attribute.name}"

class AssetAttribute(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='asset_attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value_text = models.TextField(blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    value_email = models.EmailField(null=True, blank=True)
    value_url = models.URLField(null=True, blank=True)
    value_json = models.JSONField(null=True, blank=True)
def __str__(self):
     return f"{self.attribute.name} for {self.asset.name}: {self.get_value()}"

def get_value(self):
        """ Возвращает значение атрибута в зависимости от его типа. """
        type_map = {
            Attribute.TEXT: self.value_text,
            Attribute.NUMBER: self.value_number,
            Attribute.DATE: self.value_date,
            Attribute.BOOLEAN: self.value_boolean,  # предполагается, что это поле также добавлено в модель
            Attribute.EMAIL: self.value_email,  # аналогично
            Attribute.URL: self.value_url,  # аналогично
            Attribute.JSON: self.value_json,
            # JSON поля могут требовать специальной обработки или сериализации/десериализации
            Attribute.ASSET_REFERENCE: self.value_asset_reference.name if self.value_asset_reference else None,
            Attribute.ATTRIBUTE_REFERENCE: self.value_attribute_reference.get_value() if self.value_attribute_reference else None,
        }
        return type_map.get(self.attribute.attribute_type)
class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:50]  # Вывод первых 50 символов сообщения
class Doc(models.Model):
    title = models.CharField(max_length=255)
    doc_file = models.FileField(upload_to='documents/%Y/%m/%d/')
    analyzed = models.BooleanField(default=False)
    text_content = models.TextField(blank=True, null=True)
    image_urls = models.TextField(blank=True, null=True)
    tables = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title