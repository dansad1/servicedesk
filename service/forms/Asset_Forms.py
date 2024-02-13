from django import forms
from service.models import Attribute, Asset, AssetType,AssetAttribute


class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = ['name', 'attribute_type']  # Убрано 'asset_types', если оно не используется здесь
        widgets = {
            'attribute_type': forms.Select(attrs={'class': 'form-control'}),
        }



class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'parent_asset']

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        # Предварительная инициализация формы с динамическими полями для атрибутов
        if self.instance.pk:
            for asset_attribute in self.instance.asset_attributes.all():
                field_name = f'attribute_{asset_attribute.attribute.pk}'
                field_label = asset_attribute.attribute.name
                field_value = asset_attribute.get_value()
                self.fields[field_name] = forms.CharField(initial=field_value, label=field_label, required=False)


class AssetTypeForm(forms.ModelForm):
    class Meta:
        model = AssetType
        fields = ['name', 'parent']  # Предполагаем, что у модели AssetType есть поля 'name' и 'parent'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }