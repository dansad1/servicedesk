from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Priority, SavedFilter
from .models import Company,Request,Status,Comment,RequestType,Department,PriorityDuration,StatusTransition,Role,Permission
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth import get_user_model
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address','company','role')

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'description']  # Здесь перечислите поля, которые вы хотите отображать в форме
class RequestForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    duration_in_hours = forms.IntegerField(required=False, widget=forms.HiddenInput())
    attachment = forms.FileField(required=False)

    class Meta:
        model = Request
        fields = ['title', 'description', 'assignee', 'status', 'request_type', 'due_date', 'priority']

    def __init__(self, *args, **kwargs):
        current_status = kwargs.pop('current_status', None)
        super(RequestForm, self).__init__(*args, **kwargs)

        # Styling for fields
        self.fields['priority'].widget.attrs.update({'class': 'form-control'})
        self.fields['assignee'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['request_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['due_date'].widget.attrs.update({'class': 'form-control datetimepicker-input'})

        # Make status field optional
        self.fields['status'].required = False
        self.fields['status'].empty_label = "No change"  # Label for no change option

        # Set queryset and initial value for 'status' field
        if current_status:
            valid_next_statuses = StatusTransition.objects.filter(
                from_status=current_status
            ).values_list('to_status', flat=True)
            self.fields['status'].queryset = Status.objects.filter(
                id__in=valid_next_statuses).union(Status.objects.filter(pk=current_status.pk))
            self.fields['status'].initial = current_status
        else:
            # For a new request, set a default status if needed
            default_status, created = Status.objects.get_or_create(name="Открыта")
            self.fields['status'].queryset = Status.objects.filter(pk=default_status.pk)
            self.fields['status'].initial = default_status
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'attachment']  # Добавьте 'attachment' здесь, если у вас есть такое поле
        widgets = {'text': CKEditorWidget()}
class RequestFilterForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    filter_name = forms.CharField(max_length=100, required=False)
    requester = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    assignee = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    company = forms.ModelMultipleChoiceField(queryset=Company.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    status = forms.ModelMultipleChoiceField(queryset=Status.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    created_at = forms.DateTimeField(required=False)
    updated_at = forms.DateTimeField(required=False)
    priority = forms.ModelMultipleChoiceField(queryset=Priority.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    request_type = forms.ModelMultipleChoiceField(queryset=RequestType.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)


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


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'permissions']

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        self.fields['permissions'].queryset = Permission.objects.all()

        # Динамическое добавление полей для уровней доступа
        for permission in Permission.objects.all():
            field_name = f'access_level_{permission.pk}'
            self.fields[field_name] = forms.ChoiceField(
                choices=[('global', 'Глобально'), ('company', 'Компания'), ('department', 'Отдел'), ('personal', 'Личный')],
                label=f"Уровень доступа для {permission.name}",
                required=False
            )