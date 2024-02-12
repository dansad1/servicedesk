from django import forms
from service.models import Attribute, Asset


class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = ['name', 'attribute_type', 'asset_types']
class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = ['name', 'attribute_type', 'asset_types']


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['asset_type', 'parent_asset']

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        # Динамическое добавление полей атрибутов в зависимости от типа актива
        if 'instance' in kwargs and kwargs['instance']:
            asset = kwargs['instance']
            asset_type = asset.asset_type
            attributes = asset_type.attributes.all()
            for attribute in attributes:
                field_name = 'attribute_{}'.format(attribute.id)
                self.fields[field_name] = forms.CharField(label=attribute.name, required=False)
                # Здесь может быть добавлена логика для разных типов атрибутов

