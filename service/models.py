from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from ckeditor.fields import RichTextField  # Import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test

ROLES_CHOICES = (
    ('user', 'Пользователь'),
    ('admin', 'Администратор'),
)

class Company(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название компании')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

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
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Компания')
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('Department', null=True, blank=True, on_delete=models.SET_NULL)
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.username

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField('Permission')

    def __str__(self):
        return self.name

class Permission(models.Model):
    code_name = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=50, choices=[('global', 'Global'), ('company', 'Company'), ('department', 'Department'), ('personal', 'Personal')])
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


