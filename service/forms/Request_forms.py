from datetime import timezone, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth import get_user_model
from django.forms import SelectMultiple, DateInput
from service.models import StatusTransition, Status, Comment, Request, Company, Priority, RequestType, SavedFilter, \
    FieldAccess, FieldMeta, FieldValue, CustomUser, PriorityDuration
from django.forms.widgets import Select
from django.contrib.auth.models import Group


User = get_user_model()

def generate_dynamic_form(fieldset):
    class DynamicRequestFilterForm(forms.Form):
        filter_name = forms.CharField(
            max_length=100,
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            label="Название фильтра"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in fieldset.fields.all():
                field_name = field.name.lower().replace(' ', '_')

                if field.field_type == 'text':
                    self.fields[field_name] = forms.CharField(
                        required=False,
                        label=field.name,
                        widget=forms.TextInput(attrs={'class': 'form-control'})
                    )
                elif field.field_type == 'textarea':
                    self.fields[field_name] = forms.CharField(
                        required=False,
                        label=field.name,
                        widget=forms.Textarea(attrs={'class': 'form-control'})
                    )
                elif field.field_type == 'date':
                    self.fields[field_name] = forms.DateField(
                        required=False,
                        label=field.name,
                        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
                    )
                elif field.field_type == 'file':
                    self.fields[field_name] = forms.FileField(
                        required=False,
                        label=field.name,
                        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
                    )
                elif field.field_type == 'requester':
                    self.fields[field_name] = forms.ModelChoiceField(
                        queryset=User.objects.all(),
                        required=False,
                        label=field.name,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
                elif field.field_type == 'assignee':
                    self.fields[field_name] = forms.ModelChoiceField(
                        queryset=User.objects.all(),
                        required=False,
                        label=field.name,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
                elif field.field_type == 'company':
                    self.fields[field_name] = forms.ModelChoiceField(
                        queryset=Company.objects.all(),
                        required=False,
                        label=field.name,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
                elif field.field_type == 'status':
                    self.fields[field_name] = forms.ModelChoiceField(
                        queryset=Status.objects.all(),
                        required=False,
                        label=field.name,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
                elif field.field_type == 'priority':
                    self.fields[field_name] = forms.ModelChoiceField(
                        queryset=Priority.objects.all(),
                        required=False,
                        label=field.name,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
                elif field.field_type == 'comment':
                    self.fields[field_name] = forms.CharField(
                        required=False,
                        label=field.name,
                        widget=forms.Textarea(attrs={'class': 'form-control'})
                    )

        def clean(self):
            cleaned_data = super().clean()
            cleaned_data.pop('filter_name', None)
            return cleaned_data

    return DynamicRequestFilterForm
class SavedFilterForm(forms.ModelForm):
    class Meta:
        model = SavedFilter
        fields = ['filter_name', 'filter_data']
        
        widgets = {
            'filter_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название фильтра',
            }),
            'filter_data': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите данные фильтра',
                'rows': 5,
            }),
        }


class CommentFormWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            CKEditorWidget(attrs={'class': 'form-control', 'placeholder': 'Введите комментарий'}),
            forms.ClearableFileInput(attrs={'class': 'form-control'}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(',')
        return ['', '']

    def format_output(self, rendered_widgets):
        return f"""
            <div class="form-group">
                <label for="id_comment_text">Комментарий</label>
                {rendered_widgets[0]}
            </div>
            <div class="form-group">
                <label for="id_comment_attachment">Прикрепить файл</label>
                {rendered_widgets[1]}
            </div>
        """

class CommentMultiValueField(forms.MultiValueField):
    def __init__(self, **kwargs):
        fields = [
            forms.CharField(widget=CKEditorWidget(), required=False),
            forms.FileField(required=False),
        ]
        super().__init__(fields, require_all_fields=False, **kwargs)
        self.widget = CommentFormWidget()

    def compress(self, data_list):
        if data_list:
            return data_list
        return ['', '']
class DescriptionFormWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            CKEditorWidget(attrs={'class': 'form-control', 'placeholder': 'Введите описание'}),
            forms.ClearableFileInput(attrs={'class': 'form-control'}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(',', 1)
        return ['', '']

    def format_output(self, rendered_widgets):
        return f"""
            <div class="form-group">
                <label for="id_description_text">Описание</label>
                {rendered_widgets[0]}
            </div>
            <div class="form-group">
                <label for="id_description_attachment">Прикрепить файл</label>
                {rendered_widgets[1]}
            </div>
        """
class DescriptionMultiValueField(forms.MultiValueField):
    def __init__(self, **kwargs):
        fields = [
            forms.CharField(widget=CKEditorWidget(), required=False),
            forms.FileField(required=False),
        ]
        super().__init__(fields, require_all_fields=False, **kwargs)
        self.widget = DescriptionFormWidget()

    def compress(self, data_list):
        if data_list:
            return ','.join([str(data) if data else '' for data in data_list])
        return ''


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['request_type']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        request_type = kwargs.pop('request_type', None)
        super(RequestForm, self).__init__(*args, **kwargs)

        # Set the CSS class for the request_type field
        self.fields['request_type'].widget.attrs.update({'class': 'form-select'})

        # If request_type is provided, initialize dynamic fields
        if request_type:
            self.fields['request_type'].initial = request_type
            self.fields['request_type'].disabled = True  # Make the field read-only

            for field_meta in request_type.field_set.fields.all():
                field_name = f'custom_field_{field_meta.id}'
                initial_value = self.get_initial_value(field_meta)
                field = self.get_form_field(field_meta, initial_value)
                field.required = field_meta.is_required  # Set field requirement based on FieldMeta
                self.fields[field_name] = field

            # Add the due_date custom field as read-only
            due_date_field_meta = FieldMeta.objects.filter(name='Due Date', field_type='date').first()
            if due_date_field_meta:
                due_date_field_name = f'custom_field_{due_date_field_meta.id}'
                due_date_value = self.calculate_due_date(self.instance)
                due_date_field = forms.DateTimeField(
                    label=due_date_field_meta.name,  # Set the correct field label
                    initial=due_date_value,
                    required=False,
                    widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'type': 'datetime-local'})
                )
                self.fields[due_date_field_name] = due_date_field

    def get_initial_value(self, field_meta):
        if self.instance.pk:
            try:
                field_value = FieldValue.objects.get(request=self.instance, field_meta=field_meta)
                return field_value.get_value()
            except FieldValue.DoesNotExist:
                return None
        else:
            if field_meta.field_type == 'company':
                return self.user.company if self.user and hasattr(self.user, 'company') else None
            elif field_meta.field_type == 'requester':
                return self.user
            elif field_meta.field_type == 'assignee':
                return None
            elif field_meta.default_value:
                if field_meta.field_type == 'status':
                    return get_object_or_404(Status, id=field_meta.default_value)
                elif field_meta.field_type == 'priority':
                    return get_object_or_404(Priority, id=field_meta.default_value)
                elif field_meta.field_type in ['text', 'textarea', 'number', 'date', 'boolean', 'email', 'url', 'json']:
                    return field_meta.default_value
            return None

    def get_form_field(self, field_meta, initial_value):
        field_class = {
            'text': forms.CharField,
            'textarea': forms.CharField,
            'date': forms.DateField,
            'file': forms.FileField,
            'number': forms.FloatField,
            'boolean': forms.BooleanField,
            'email': forms.EmailField,
            'url': forms.URLField,
            'json': forms.JSONField,
            'status': forms.ModelChoiceField,
            'company': forms.ModelChoiceField,
            'priority': forms.ModelChoiceField,
            'requester': forms.ModelChoiceField,
            'assignee': forms.ModelChoiceField,
            'comment': CommentMultiValueField,
            'description': DescriptionMultiValueField,
        }.get(field_meta.field_type, forms.CharField)

        if field_meta.field_type in ['status', 'company', 'priority', 'requester', 'assignee']:
            queryset = self.get_queryset(field_meta.field_type)
            return field_class(
                label=field_meta.name,  # Set the correct field label
                required=field_meta.is_required,
                queryset=queryset,
                initial=initial_value,
                widget=forms.Select(attrs={'class': 'form-select'})
            )
        else:
            widget = self.get_widget(field_meta)
            return field_class(
                label=field_meta.name,  # Set the correct field label
                required=field_meta.is_required,
                initial=initial_value,
                widget=widget
            )

    def get_widget(self, field_meta):
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'textarea': forms.Textarea(attrs={'class': 'form-textarea'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'boolean': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'json': forms.Textarea(attrs={'class': 'form-textarea'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'requester': forms.Select(attrs={'class': 'form-select'}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
            'comment': CommentFormWidget(),
            'description': DescriptionFormWidget(),
        }
        return widgets.get(field_meta.field_type, forms.TextInput(attrs={'class': 'form-control'}))

    def get_queryset(self, field_type):
        querysets = {
            'status': Status.objects.all(),
            'company': Company.objects.all(),
            'priority': Priority.objects.all(),
            'requester': CustomUser.objects.all(),
            'assignee': CustomUser.objects.all(),
        }
        return querysets.get(field_type, CustomUser.objects.none())

    def calculate_due_date(self, request_instance):
        """Calculates and returns the due_date value for the custom field based on priority, accurate to minutes."""
        if not request_instance.created_at:
            request_instance.created_at = timezone.now()  # Set current date and time if not set

        priority_value = request_instance.field_values.filter(field_meta__field_type='priority').first()
        if priority_value:
            priority_duration = PriorityDuration.objects.filter(
                request_type=request_instance.request_type,
                priority=priority_value.value_priority
            ).first()
            if priority_duration:
                return request_instance.created_at + timedelta(hours=priority_duration.duration_in_hours)
        return None

    def save(self, commit=True):
        instance = super(RequestForm, self).save(commit=False)

        if not instance.created_at:
            instance.created_at = timezone.now()  # Set current date and time if not set

        if commit:
            instance.save()  # Save the Request first to get the primary key

            # Save the due_date custom field after the Request has been saved
            due_date_field_meta = FieldMeta.objects.filter(name='Due Date', field_type='date').first()
            if due_date_field_meta:
                due_date_value = self.calculate_due_date(instance)
                FieldValue.objects.update_or_create(
                    request=instance,
                    field_meta=due_date_field_meta,
                    defaults={'value_date': due_date_value}
                )

            # Save other custom fields
            for field_name, field_value in self.cleaned_data.items():
                if field_name.startswith('custom_field_'):
                    field_id = int(field_name.split('_')[-1])
                    field_meta = get_object_or_404(FieldMeta, id=field_id)
                    if field_meta.field_type != 'comment':
                        field_value_obj, created = FieldValue.objects.get_or_create(
                            request=instance,
                            field_meta=field_meta
                        )
                        field_value_obj.set_value(field_value)
                        field_value_obj.save()
                    else:
                        existing_comment = Comment.objects.filter(
                            request=instance,
                            author=self.user,
                            text=field_value[0],
                            attachment=field_value[1]
                        ).first()
                        if not existing_comment and (field_value[0].strip() or field_value[1]):
                            comment = Comment(
                                request=instance,
                                author=self.user,
                                text=field_value[0],
                                attachment=field_value[1]
                            )
                            comment.save()
        return instance