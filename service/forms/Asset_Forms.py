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

        # Добавление динамических полей для атрибутов при редактировании
        if self.instance.pk:
            self.init_dynamic_fields()
        # Подготовка динамических полей для нового актива на основе родителя или типа актива
        else:
            self.prepare_fields_based_on_type_or_parent()

    def init_dynamic_fields(self):
        for asset_attribute in self.instance.asset_attributes.all():
            self.add_dynamic_field(asset_attribute)

    def prepare_fields_based_on_type_or_parent(self):
        # Наследование атрибутов от родительского актива
        if 'parent_asset' in self.initial:
            parent_id = self.initial['parent_asset']
            parent_asset = Asset.objects.get(pk=parent_id)
            self.inherit_attributes(parent_asset.asset_attributes.all())
        # Наследование атрибутов от типа актива
        elif 'asset_type' in self.initial:
            asset_type_id = self.initial['asset_type']
            asset_type = AssetType.objects.get(pk=asset_type_id)
            self.inherit_attributes(asset_type.assettypeattribute_set.all(), default=True)

    def add_dynamic_field(self, asset_attribute, default_value=None):
        field_name = f'attribute_{asset_attribute.attribute.pk}'
        field_value = asset_attribute.get_value() if default_value is None else default_value
        field_class, widget_class = self.determine_field_class(asset_attribute.attribute.attribute_type)
        self.fields[field_name] = field_class(
            initial=field_value,
            label=asset_attribute.attribute.name,
            widget=widget_class(attrs={'class': 'form-control'}),
            required=False
        )

    def inherit_attributes(self, attributes, default=False):
        for attr in attributes:
            initial_value = "" if default else attr.get_value()
            self.add_dynamic_field(attr, initial_value)

    def determine_field_class(self, attribute_type):
        """ Отображает типы атрибутов на поля формы и виджеты. """
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
        return type_map.get(attribute_type, (forms.CharField, forms.TextInput))

    def get_value_from_type(self, attribute_type):
        """ Возвращает значение по умолчанию для типа атрибута """
        defaults = {
            Attribute.TEXT: '',
            Attribute.NUMBER: 0.0,
            Attribute.DATE: None,
            Attribute.BOOLEAN: False,
            Attribute.EMAIL: '',
            Attribute.URL: '',
            Attribute.JSON: {},
            Attribute.ASSET_REFERENCE: None,
            Attribute.ATTRIBUTE_REFERENCE: None,
        }
        return defaults.get(attribute_type)


