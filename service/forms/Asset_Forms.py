from django import forms
from service.models import Attribute, Asset, AssetType,AssetAttribute,AssetTypeAttribute


class AssetTypeForm(forms.ModelForm):
    class Meta:
        model = AssetType
        fields = ['name', 'parent']  # Основные поля формы
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AssetTypeForm, self).__init__(*args, **kwargs)
        # Если родительский тип не выбран, отображаем пустой вариант
        self.fields['parent'].empty_label = "Без родительского типа"
class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = ['name', 'attribute_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'attribute_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AttributeForm, self).__init__(*args, **kwargs)
        # Логика для добавления поля значения в зависимости от типа атрибута
        attribute_instance = kwargs.get('instance')
        if attribute_instance:
            attribute_type = attribute_instance.attribute_type

            # Добавляем соответствующее поле для значения атрибута
            if attribute_type == Attribute.TEXT:
                self.fields['value'] = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
            elif attribute_type == Attribute.NUMBER:
                self.fields['value'] = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
            elif attribute_type == Attribute.DATE:
                self.fields['value'] = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=False)
            elif attribute_type == Attribute.BOOLEAN:
                self.fields['value'] = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
            elif attribute_type == Attribute.EMAIL:
                self.fields['value'] = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), required=False)
            elif attribute_type == Attribute.URL:
                self.fields['value'] = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control'}), required=False)
            elif attribute_type == Attribute.JSON:
                self.fields['value'] = forms.JSONField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)

    def save(self, commit=True):
        instance = super(AttributeForm, self).save(commit=False)

        # Логика сохранения значения атрибута в зависимости от его типа
        value = self.cleaned_data.get('value', None)
        if instance.attribute_type == Attribute.TEXT:
            instance.value_text = value
        elif instance.attribute_type == Attribute.NUMBER:
            instance.value_number = value
        elif instance.attribute_type == Attribute.DATE:
            instance.value_date = value
        elif instance.attribute_type == Attribute.BOOLEAN:
            instance.value_boolean = value
        elif instance.attribute_type == Attribute.EMAIL:
            instance.value_email = value
        elif instance.attribute_type == Attribute.URL:
            instance.value_url = value
        elif instance.attribute_type == Attribute.JSON:
            instance.value_json = value

        if commit:
            instance.save()
        return instance

class AssetTypeAttributeForm(forms.ModelForm):
    class Meta:
        model = AssetTypeAttribute
        fields = ['attribute']
        widgets = {
            'attribute': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AssetTypeAttributeForm, self).__init__(*args, **kwargs)
        # Можно добавить дополнительную логику для динамической обработки атрибутов
class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'parent_asset']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_type': forms.Select(attrs={'class': 'form-control'}),
            'parent_asset': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        # Добавление пустого значения для родительского актива
        self.fields['parent_asset'].empty_label = "Без родительского актива"