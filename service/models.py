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
    code_name = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class GroupPermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    custompermission = models.ForeignKey(CustomPermission, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.group.name} - {self.custompermission.name}"
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
            'select': self.value_text,
            'number': self.value_number,
            'date': self.value_date,
            'boolean': self.value_boolean,
            'email': self.value_email,
            'url': self.value_url,
            'json': self.value_json,
            'status': self.value_status.name if self.value_status else None,
            'company': self.value_company.name if self.value_company else None,
            'priority': self.value_priority.name if self.value_priority else None,
            'requester': self.value_requester.username if self.value_requester else None,
            'assignee': self.value_assignee.username if self.value_assignee else None,
            'request_type': self.value_request_type.name if self.value_request_type else None,
            'file': self.value_file.name if self.value_file else None,
        }
        return type_map.get(self.field_meta.field_type)
class Request(models.Model):
    request_type = models.ForeignKey(RequestType, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.id}"
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

class Event(models.Model):
    EVENT_CHOICES = [
        ('create_request', 'Создание заявки'),
        ('update_request', 'Изменение полей заявки'),
        ('add_comment', 'Добавление комментария'),
        ('deadline_expiration', 'Истечение срока заявки'),
        ('status_change', 'Смена статуса заявки'),
    ]
    name = models.CharField(max_length=255, choices=EVENT_CHOICES, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.get_name_display()

class NotificationSetting(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='notification_settings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email_template = models.TextField(blank=True, null=True)  # Пустой шаблон означает неактивное уведомление

    def __str__(self):
        return f"{self.group.name} - {self.event.name}"
class NotificationTemplate(models.Model):
    type = models.CharField(max_length=100, choices=[('email', 'Email'), ('sms', 'SMS'), ('push', 'Push Notification')])
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    body = RichTextUploadingField(help_text="Используйте инструменты редактора для форматирования текста.")

    def __str__(self):
        return self.name
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