from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import DateInput, SelectMultiple

from .models import CustomUser, Priority, SavedFilter, CustomPermission, GroupPermission
from .models import Company,Request,Status,Comment,RequestType,Department,PriorityDuration,StatusTransition,EmailSettings
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address','company','group')
class CustomUserEditForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'company', 'group',)
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'description']

class RequestForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    duration_in_hours = forms.IntegerField(required=False, widget=forms.HiddenInput())
    attachment = forms.FileField(required=False)
    request_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Request
        # Исключаем 'request_type' из списка отображаемых полей
        fields = ['title', 'description', 'assignee', 'status', 'due_date', 'priority','request_type']

    def __init__(self, *args, **kwargs):
        current_status = kwargs.pop('current_status', None)
        super(RequestForm, self).__init__(*args, **kwargs)

        # Styling for fields
        for field_name in ['priority', 'assignee', 'status', 'due_date']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
        self.fields['due_date'].widget.attrs.update({'class': 'form_control datetimepicker-input'})

        # Make status field optional and set initial values
        self.fields['status'].required = False
        self.fields['status'].empty_label = "No change"

        # Adjust status field based on current status
        self.adjust_status_field(current_status)

    def adjust_status_field(self, current_status):
        if current_status:
            # Limit status choices to valid next statuses
            valid_next_statuses = StatusTransition.objects.filter(
                from_status=current_status
            ).values_list('to_status', flat=True)
            self.fields['status'].queryset = Status.objects.filter(
                id__in=valid_next_statuses
            ).union(Status.objects.filter(pk=current_status.pk))
            self.fields['status'].initial = current_status
        else:
            # Set a default status for new requests
            default_status, _ = Status.objects.get_or_create(name="Открыта")
            self.fields['status'].queryset = Status.objects.filter(pk=default_status.pk)
            self.fields['status'].initial = default_status

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'attachment']  # Предполагается, что поля 'text' и 'attachment' определены в модели Comment
        widgets = {
            'text': CKEditorWidget(),  # Использует виджет CKEditor для поля 'text'
            # Для поля 'attachment' будет использоваться виджет по умолчанию, если не указано иное
        }

class RequestFilterForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    filter_name = forms.CharField(max_length=100, required=False)

    requester = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    assignee = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    company = forms.ModelMultipleChoiceField(
        queryset=Company.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    status = forms.ModelMultipleChoiceField(
        queryset=Status.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    created_at = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )

    updated_at = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )

    priority = forms.ModelMultipleChoiceField(
        queryset=Priority.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    request_type = forms.ModelMultipleChoiceField(
        queryset=RequestType.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )
class SavedFilterForm(forms.ModelForm):
    class Meta:
        model = SavedFilter
        fields = ['filter_name', 'filter_data']

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
class RequestTypeForm(forms.ModelForm):
    class Meta:
        model = RequestType
        fields = ['name', 'description']
class PriorityForm(forms.ModelForm):
    class Meta:
        model = Priority
        fields = ['name']
class PriorityDurationForm(forms.ModelForm):
    class Meta:
        model = PriorityDuration
        fields = ['request_type', 'priority', 'duration_in_hours']
class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name', 'color', 'description']

class StatusTransitionForm(forms.ModelForm):
    class Meta:
        model = StatusTransition
        fields = ['from_status', 'to_status', 'allowed_groups']


class GroupForm(forms.ModelForm):
    action_permissions = forms.ModelMultipleChoiceField(
        queryset=CustomPermission.objects.filter(code_name__startswith='action_'),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Разрешения Действий'
    )
    section_permissions = forms.ModelMultipleChoiceField(
        queryset=CustomPermission.objects.filter(code_name__startswith='section_'),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Разрешения для Разделов'
    )

    class Meta:
        model = Group
        fields = ['name']

    def __init__(self, *args, **kwargs):
        group = kwargs.get('instance')
        super(GroupForm, self).__init__(*args, **kwargs)

        # Инициализация начальных значений для разрешений действий
        if group:
            self.initial['action_permissions'] = group.grouppermission_set.filter(
                custompermission__code_name__startswith='action_'
            ).values_list('custompermission__id', flat=True)
            # Инициализация начальных значений для разрешений разделов
            self.initial['section_permissions'] = group.grouppermission_set.filter(
                custompermission__code_name__startswith='section_'
            ).values_list('custompermission__id', flat=True)

        # Добавляем динамические поля для уровней доступа
        for permission in CustomPermission.objects.filter(code_name__startswith='action_'):
            field_name = f'access_level_{permission.id}'
            self.fields[field_name] = forms.ChoiceField(
                choices=[('global', 'Global'), ('company', 'Company'), ('department', 'Department'), ('personal', 'Personal')],
                required=False,
                label='Уровень доступа для ' + permission.name
            )
            # Установка начального значения для уровня доступа, если группа уже имеет это разрешение
            if group:
                access_level = group.grouppermission_set.filter(custompermission=permission).first()
                if access_level:
                    self.initial[field_name] = access_level.access_level
class EmailSettingsForm(forms.ModelForm):
    CONNECTION_CHOICES = [
        ('tls', 'TLS'),
        ('ssl', 'SSL'),
    ]

    connection_type = forms.ChoiceField(
        label="Use TLS or SSL",
        choices=CONNECTION_CHOICES,
        widget=forms.RadioSelect,
        initial='tls'
    )

    test_email_to = forms.EmailField(required=False, help_text="Введите адрес для тестового письма")
    class Meta:
     model = EmailSettings
     fields = ['server', 'port', 'login', 'password', 'email_from', 'connection_type']
     widgets = {
        'password': forms.PasswordInput(),  # Скрыть ввод пароля
    }

     def clean(self):
         cleaned_data = super().clean()
         connection_type = cleaned_data.get("connection_type")
         if connection_type == 'tls':
             cleaned_data['use_tls'] = True
             cleaned_data['use_ssl'] = False
         elif connection_type == 'ssl':
             cleaned_data['use_tls'] = False
             cleaned_data['use_ssl'] = True
         return cleaned_data