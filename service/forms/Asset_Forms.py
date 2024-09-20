from django import forms
from service.models import Attribute, Asset, AssetType,AssetAttribute,AssetTypeAttribute


from django import forms
from service.models import AssetType, Attribute

class AssetTypeForm(forms.ModelForm):
    class Meta:
        model = AssetType
        fields = ['name', 'parent', 'components']  # Основные поля формы
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'components': forms.SelectMultiple(attrs={'class': 'form-control'}),  # Поле для выбора компонентов
        }

    def __init__(self, *args, **kwargs):
        super(AssetTypeForm, self).__init__(*args, **kwargs)
        # Установка пустого значения для родительского типа
        self.fields['parent'].empty_label = "Без родительского типа"

    def save(self, commit=True):
        """
        Переопределяем метод сохранения, чтобы работать с компонентами
        """
        instance = super(AssetTypeForm, self).save(commit=False)
        # Логика копирования атрибутов и работы с компонентами будет вынесена в сервисные функции.
        if commit:
            instance.save()
            self.save_m2m()  # Сохраняем ManyToMany связи для компонентов
        return instance

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
        attribute_instance = kwargs.get('instance')

        # Если есть экземпляр атрибута (редактирование)
        if attribute_instance:
            attribute_type = attribute_instance.attribute_type
        else:
            # Получаем тип атрибута из POST данных, если он был выбран
            attribute_type = self.data.get('attribute_type', None)

        # Добавляем поле для значения, если тип атрибута определён
        if attribute_type:
            self.add_value_field(attribute_type)

    def add_value_field(self, attribute_type):
        """Динамически добавляет поле для значения атрибута."""
        field_options = {'class': 'form-control'}
        if attribute_type == Attribute.TEXT:
            self.fields['value'] = forms.CharField(widget=forms.TextInput(attrs=field_options), required=False)
        elif attribute_type == Attribute.NUMBER:
            self.fields['value'] = forms.FloatField(widget=forms.NumberInput(attrs=field_options), required=False)
        elif attribute_type == Attribute.DATE:
            self.fields['value'] = forms.DateField(widget=forms.DateInput(attrs={**field_options, 'type': 'date'}), required=False)
        elif attribute_type == Attribute.BOOLEAN:
            self.fields['value'] = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
        elif attribute_type == Attribute.EMAIL:
            self.fields['value'] = forms.EmailField(widget=forms.EmailInput(attrs=field_options), required=False)
        elif attribute_type == Attribute.URL:
            self.fields['value'] = forms.URLField(widget=forms.URLInput(attrs=field_options), required=False)
        elif attribute_type == Attribute.JSON:
            self.fields['value'] = forms.JSONField(widget=forms.Textarea(attrs=field_options), required=False)

    def save(self, commit=True):
        instance = super(AttributeForm, self).save(commit=False)
        value = self.cleaned_data.get('value')

        # Сохранение значения в зависимости от его типа
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
        # Можно добавить дополнительную логику для отображения атрибутов
class AssetAttributeForm(forms.ModelForm):
    class Meta:
        model = AssetAttribute
        fields = ['attribute']
        widgets = {
            'attribute': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AssetAttributeForm, self).__init__(*args, **kwargs)
        asset_attribute_instance = kwargs.get('instance')

        # Если экземпляр существует (редактирование), получаем тип атрибута
        if asset_attribute_instance:
            attribute_type = asset_attribute_instance.attribute.attribute_type
        else:
            # Если POST данные, получаем атрибут из них, чтобы определить его тип
            attribute_id = self.data.get('attribute')
            if attribute_id:
                attribute = Attribute.objects.get(pk=attribute_id)
                attribute_type = attribute.attribute_type
            else:
                attribute_type = None

        # Если тип атрибута известен, добавляем поле для значения
        if attribute_type:
            self.add_value_field(attribute_type)

    def add_value_field(self, attribute_type):
        """Динамически добавляет поле для значения в зависимости от типа атрибута."""
        field_options = {'class': 'form-control'}
        if attribute_type == Attribute.TEXT:
            self.fields['value'] = forms.CharField(widget=forms.TextInput(attrs=field_options), required=False)
        elif attribute_type == Attribute.NUMBER:
            self.fields['value'] = forms.FloatField(widget=forms.NumberInput(attrs=field_options), required=False)
        elif attribute_type == Attribute.DATE:
            self.fields['value'] = forms.DateField(widget=forms.DateInput(attrs={**field_options, 'type': 'date'}), required=False)
        elif attribute_type == Attribute.BOOLEAN:
            self.fields['value'] = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
        elif attribute_type == Attribute.EMAIL:
            self.fields['value'] = forms.EmailField(widget=forms.EmailInput(attrs=field_options), required=False)
        elif attribute_type == Attribute.URL:
            self.fields['value'] = forms.URLField(widget=forms.URLInput(attrs=field_options), required=False)
        elif attribute_type == Attribute.JSON:
            self.fields['value'] = forms.JSONField(widget=forms.Textarea(attrs=field_options), required=False)

    def save(self, commit=True):
        instance = super(AssetAttributeForm, self).save(commit=False)
        value = self.cleaned_data.get('value')

        # Сохраняем значение в зависимости от типа атрибута
        attribute_type = instance.attribute.attribute_type

        if attribute_type == Attribute.TEXT:
            instance.value_text = value
        elif attribute_type == Attribute.NUMBER:
            instance.value_number = value
        elif attribute_type == Attribute.DATE:
            instance.value_date = value
        elif attribute_type == Attribute.BOOLEAN:
            instance.value_boolean = value
        elif attribute_type == Attribute.EMAIL:
            instance.value_email = value
        elif attribute_type == Attribute.URL:
            instance.value_url = value
        elif attribute_type == Attribute.JSON:
            instance.value_json = value

        if commit:
            instance.save()
        return instance
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

        # Добавляем пустое значение для родительского актива
        self.fields['parent_asset'].empty_label = "Без родительского актива"

        # Если есть инстанс актива, наследуем атрибуты
        if self.instance.pk:
            self.inherit_attributes()
        elif 'parent_asset' in self.data or 'asset_type' in self.data:
            # Если создаем новый актив, пытаемся наследовать атрибуты при выборе родителя или типа актива
            self.inherit_attributes_for_creation()

    def inherit_attributes_for_creation(self):
        """Наследование атрибутов при создании актива от типа или родительского актива."""
        asset_attributes = {}

        # Наследуем атрибуты от родительского актива
        parent_asset_id = self.data.get('parent_asset')
        if parent_asset_id:
            parent_asset = Asset.objects.get(id=parent_asset_id)
            parent_attributes = parent_asset.asset_attributes.all()
            for attr in parent_attributes:
                asset_attributes[attr.attribute.pk] = attr

        # Наследуем атрибуты от типа актива
        asset_type_id = self.data.get('asset_type')
        if asset_type_id:
            asset_type_attributes = AssetTypeAttribute.objects.filter(asset_type_id=asset_type_id)
            for type_attr in asset_type_attributes:
                if type_attr.attribute.pk not in asset_attributes:
                    asset_attributes[type_attr.attribute.pk] = AssetAttribute(
                        asset=None, attribute=type_attr.attribute, value_text=None
                    )

        # Создаем поля для каждого атрибута
        for attribute_pk, asset_attr in asset_attributes.items():
            field_name = f'attribute_{attribute_pk}_value'
            field_value = asset_attr.get_value()
            field_class, widget_class = self.get_field_class_and_widget(asset_attr.attribute.attribute_type)
            self.fields[field_name] = field_class(
                initial=field_value,
                label=asset_attr.attribute.name,
                widget=widget_class(attrs={'class': 'form-control'}),
                required=False
            )

    def inherit_attributes(self):
        """Наследуем атрибуты для уже существующего актива."""
        asset_attributes = {attr.attribute.pk: attr for attr in self.instance.asset_attributes.all()}

        # Наследуем атрибуты от родительского актива
        if self.instance.parent_asset:
            parent_attributes = self.instance.parent_asset.asset_attributes.all()
            for attr in parent_attributes:
                if attr.attribute.pk not in asset_attributes:
                    asset_attributes[attr.attribute.pk] = attr

        # Наследуем атрибуты от типа актива
        if self.instance.asset_type:
            type_attributes = AssetTypeAttribute.objects.filter(asset_type=self.instance.asset_type)
            for type_attr in type_attributes:
                if type_attr.attribute.pk not in asset_attributes:
                    asset_attributes[type_attr.attribute.pk] = AssetAttribute(
                        asset=self.instance, attribute=type_attr.attribute, value_text=None
                    )

        # Создаем динамические поля для каждого атрибута
        for attribute_pk, asset_attr in asset_attributes.items():
            field_name = f'attribute_{attribute_pk}_value'
            field_value = asset_attr.get_value()
            field_class, widget_class = self.get_field_class_and_widget(asset_attr.attribute.attribute_type)
            self.fields[field_name] = field_class(
                initial=field_value,
                label=asset_attr.attribute.name,
                widget=widget_class(attrs={'class': 'form-control'}),
                required=False
            )

    def get_field_class_and_widget(self, attribute_type):
        """Возвращает класс поля и виджет в зависимости от типа атрибута."""
        type_map = {
            Attribute.TEXT: (forms.CharField, forms.TextInput),
            Attribute.NUMBER: (forms.FloatField, forms.NumberInput),
            Attribute.DATE: (forms.DateField, forms.DateInput),
            Attribute.BOOLEAN: (forms.BooleanField, forms.CheckboxInput),
            Attribute.EMAIL: (forms.EmailField, forms.EmailInput),
            Attribute.URL: (forms.URLField, forms.URLInput),
            Attribute.JSON: (forms.JSONField, forms.Textarea),
        }
        return type_map.get(attribute_type, (forms.CharField, forms.TextInput))

    def save(self, commit=True):
        # Сохраняем основной объект актива
        instance = super(AssetForm, self).save(commit=False)
        if commit:
            instance.save()

        # Сохраняем атрибуты актива
        for field_name in self.cleaned_data:
            if field_name.startswith('attribute_'):
                attribute_id = int(field_name.split('_')[1])
                value = self.cleaned_data[field_name]

                asset_attr, created = AssetAttribute.objects.get_or_create(
                    asset=instance,
                    attribute_id=attribute_id,
                    defaults={'value_text': value}
                )

                if not created:
                    if asset_attr.attribute.attribute_type == Attribute.TEXT:
                        asset_attr.value_text = value
                    elif asset_attr.attribute.attribute_type == Attribute.NUMBER:
                        asset_attr.value_number = value
                    elif asset_attr.attribute.attribute_type == Attribute.DATE:
                        asset_attr.value_date = value
                    elif asset_attr.attribute.attribute_type == Attribute.BOOLEAN:
                        asset_attr.value_boolean = value == 'on'
                    asset_attr.save()

        return instance
