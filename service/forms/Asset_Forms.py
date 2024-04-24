from django import forms
from service.models import Attribute, Asset, AssetType,AssetAttribute


class AssetTypeForm(forms.ModelForm):
    class Meta:
        model = AssetType
        fields = ['name', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AssetTypeForm, self).__init__(*args, **kwargs)
        # Добавление пустого выбора для поля 'parent' для поддержки создания корневых типов активов
        self.fields['parent'].empty_label = "Выберите родительский тип (если необходимо)"
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
        # Здесь можно добавить любую специфическую логику, например, настройку начальных значений или условную логику отображения полей

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'parent_asset']

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        if self.instance.pk:  # Only if the asset instance has been saved (editing)
            for asset_attribute in self.instance.asset_attributes.all():
                field_name = f'attribute_{asset_attribute.attribute.pk}'
                field_label = asset_attribute.attribute.name
                field_value = asset_attribute.get_value()

                # Dynamically add fields based on attribute type
                if asset_attribute.attribute.attribute_type == Attribute.TEXT:
                    self.fields[field_name] = forms.CharField(
                        initial=field_value, label=field_label, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
                elif asset_attribute.attribute.attribute_type == Attribute.NUMBER:
                    self.fields[field_name] = forms.FloatField(
                        initial=field_value, label=field_label, widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
                elif asset_attribute.attribute.attribute_type == Attribute.DATE:
                    self.fields[field_name] = forms.DateField(
                        initial=field_value, label=field_label, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=False)
                elif asset_attribute.attribute.attribute_type == Attribute.BOOLEAN:
                    self.fields[field_name] = forms.BooleanField(
                        initial=bool(field_value), label=field_label, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
                elif asset_attribute.attribute.attribute_type == Attribute.EMAIL:
                    self.fields[field_name] = forms.EmailField(
                        initial=field_value, label=field_label, widget=forms.EmailInput(attrs={'class': 'form-control'}), required=False)
                elif asset_attribute.attribute.attribute_type == Attribute.URL:
                    self.fields[field_name] = forms.URLField(
                        initial=field_value, label=field_label, widget=forms.URLInput(attrs={'class': 'form-control'}), required=False)
                elif asset_attribute.attribute.attribute_type == Attribute.JSON:
                    self.fields[field_name] = forms.JSONField(
                        initial=field_value, label=field_label, widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
                elif asset_attribute.attribute.attribute_type == Attribute.ASSET_REFERENCE:
                    self.fields[field_name] = forms.ModelChoiceField(
                        queryset=Asset.objects.all(), initial=asset_attribute.value_asset_reference, label=field_label,
                        widget=forms.Select(attrs={'class': 'form-control'}), required=False)
                elif asset_attribute.attribute.attribute_type == Attribute.ATTRIBUTE_REFERENCE:
                    self.fields[field_name] = forms.ModelChoiceField(
                        queryset=AssetAttribute.objects.filter(asset=self.instance),
                        initial=asset_attribute.value_attribute_reference, label=field_label,
                        widget=forms.Select(attrs={'class': 'form-control'}), required=False)


