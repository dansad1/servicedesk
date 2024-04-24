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
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_type': forms.Select(attrs={'class': 'form-control'}),
            'parent_asset': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)

        # Check if we are editing an existing asset (it has a primary key)
        if self.instance.pk:
            # Iterate over all attributes linked to this asset
            for asset_attribute in self.instance.asset_attributes.all():
                field_name = f'attribute_{asset_attribute.attribute.pk}'
                field_label = asset_attribute.attribute.name
                field_value = asset_attribute.get_value()

                # Determine the field type based on the attribute's specified type
                field_class, widget_class = self.determine_field_class(asset_attribute.attribute.attribute_type)

                # Create and add the field to the form
                self.fields[field_name] = field_class(
                    initial=field_value, label=field_label,
                    widget=widget_class(attrs={'class': 'form-control'}),
                    required=False
                )

    def determine_field_class(self, attribute_type):
        """ Map attribute types to form fields and widgets. """
        type_map = {
            Attribute.TEXT: (forms.CharField, forms.TextInput),
            Attribute.NUMBER: (forms.FloatField, forms.NumberInput),
            Attribute.DATE: (forms.DateField, forms.DateInput),
            Attribute.BOOLEAN: (forms.BooleanField, forms.CheckboxInput),
            Attribute.EMAIL: (forms.EmailField, forms.EmailInput),
            Attribute.URL: (forms.URLField, forms.URLInput),
            Attribute.JSON: (forms.JSONField, forms.Textarea),
            Attribute.ASSET_REFERENCE: (forms.ModelChoiceField, forms.Select),
            Attribute.ATTRIBUTE_REFERENCE: (forms.ModelChoiceField, forms.Select),
        }
        field_class, widget_class = type_map[attribute_type]
        return field_class, widget_class



