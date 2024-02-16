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

from servicedesk import settings


class Company(models.Model):
    # Общие данные
    name = models.CharField(_("Название компании"), max_length=255, unique=True)
    region = models.CharField(_("Регион"), max_length=255)

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
class Department(models.Model):
    name = models.CharField(max_length=200)
    company = models.ForeignKey(Company, related_name='departments', on_delete=models.CASCADE)
    parent_department = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subdepartments')


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
class CustomPermission(models.Model):
    code_name = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class GroupPermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    custompermission = models.ForeignKey(CustomPermission, on_delete=models.CASCADE)
    access_level = models.CharField(
        max_length=50,
        choices=[('global', 'Global'), ('company', 'Company'), ('department', 'Department'), ('personal', 'Personal')],
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.group.name} - {self.custom_permission.name} - {self.access_level}"
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

class RequestType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
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
class Request(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='requests')
    assignee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, blank=True)
    request_type = models.ForeignKey(RequestType, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)

    def set_due_date(self):
        duration = PriorityDuration.objects.filter(
            priority=self.priority,
            request_type=self.request_type).first()

        if duration:
            self.due_date = timezone.now() + timezone.timedelta(hours=duration.duration_in_hours)

    def save(self, *args, **kwargs):
        if not self.id:  # только при первом сохранении
            self.set_due_date()

            # Установить статус "Открыта" по умолчанию
            open_status = Status.objects.get_or_create(name='Открыта')[0]
            self.status = open_status

        super(Request, self).save(*args, **kwargs)
    def __str__(self):
        return self.title
class Comment(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = RichTextUploadingField()
    attachment = models.FileField(upload_to='comments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    content = RichTextUploadingField()  # Use RichTextUploadingField for rich text content

    def __str__(self):
        return f'Comment by {self.author.username} on {self.request.title}'
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
class GroupEventNotification(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='event_notifications')
    event = models.CharField(max_length=255)
    email_template = models.TextField()

    def __str__(self):
        return f"Уведомление для группы '{self.group.name}' на событие '{self.event}'"
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

class Attribute(models.Model):
    TEXT = 'text'
    NUMBER = 'number'
    DATE = 'date'
    ASSET_REFERENCE = 'asset_ref'
    ATTRIBUTE_REFERENCE = 'attr_ref'

    ATTRIBUTE_TYPES = [
        (TEXT, 'Text'),
        (NUMBER, 'Number'),
        (DATE, 'Date'),
        (ASSET_REFERENCE, 'Asset Reference'),
        (ATTRIBUTE_REFERENCE, 'Attribute Reference'),
    ]

    name = models.CharField(max_length=255)
    attribute_type = models.CharField(max_length=50, choices=ATTRIBUTE_TYPES)
    asset_types = models.ManyToManyField(AssetType, related_name='attributes')

class Asset(models.Model):
    name = models.CharField(max_length=255, default='Default Name')
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE, related_name='assets')
    parent_asset = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='components')

    def __str__(self):
        return self.name
class AssetAttribute(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='asset_attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value_text = models.TextField(null=True, blank=True)
    value_number = models.FloatField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)
    value_asset_reference = models.ForeignKey(Asset, null=True, blank=True, related_name='referenced_by', on_delete=models.SET_NULL)
    value_attribute_reference = models.ForeignKey('self', null=True, blank=True, related_name='referenced_attributes', on_delete=models.SET_NULL)
    def __str__(self):
        return f"{self.attribute.name} for {self.asset.name}: {self.get_value()}"


def get_value(self):
    """Возвращает значение атрибута в зависимости от его типа."""
    value_mapping = {
        'text': self.value_text,
        'number': self.value_number,
        'date': str(self.value_date) if self.value_date else None,
        'asset_ref': self.value_asset_reference.name if self.value_asset_reference else None,
        'attr_ref': self.value_attribute_reference.value_text if self.value_attribute_reference else None,
    }
    return value_mapping.get(self.attribute.attribute_type)


