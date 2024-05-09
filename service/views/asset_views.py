from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from service.forms.Asset_Forms import AssetForm
from service.models import AssetAttribute, Attribute, Asset, AssetTypeAttribute


def create_asset(request):
    form = AssetForm(request.POST or None)
    if form.is_valid():
        asset = form.save(commit=False)
        asset.save()  # Сохраняем актив, чтобы можно было добавить атрибуты

        # Наследование атрибутов от родителя или типа актива
        if asset.parent_asset:
            inherit_attributes_from_parent(asset, asset.parent_asset)
        else:
            inherit_attributes_from_type(asset, asset.asset_type)

        return redirect('asset_list')

    return render(request, 'assets/create_asset.html', {'form': form})


def inherit_attributes_from_parent(asset, parent_asset):
    parent_attributes = AssetAttribute.objects.filter(asset=parent_asset)
    for attr in parent_attributes:
        AssetAttribute.objects.create(asset=asset, **attr.get_values())


def inherit_attributes_from_type(asset, asset_type):
    type_attributes = AssetTypeAttribute.objects.filter(asset_type=asset_type)
    for type_attr in type_attributes:
        AssetAttribute.objects.create(
            asset=asset,
            attribute=type_attr.attribute,
            value_text=get_default_value_for_type(type_attr.attribute.attribute_type)
        )


def get_default_value_for_type(attribute_type):
    default_values = {
        'text': '', 'number': 0, 'date': None,
        'boolean': False, 'email': '', 'url': '',
        'json': {}, 'asset_ref': None, 'attr_ref': None
    }
    return default_values.get(attribute_type, '')
def edit_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    form = AssetForm(request.POST or None, instance=asset)
    if form.is_valid():
        form.save()
        update_asset_attributes(request.POST, asset)
        return redirect('assets_list')
    return render(request, 'assets/asset_edit.html', {'form': form, 'asset': asset})

def update_asset_attributes(post_data, asset):
    for name, value in post_data.items():
        if name.startswith('attribute_'):
            attribute_id = name.split('_')[1]
            attribute = Attribute.objects.get(pk=attribute_id)
            asset_attr, created = AssetAttribute.objects.get_or_create(asset=asset, attribute=attribute)
            if not created:
                setattr(asset_attr, f'value_{attribute.attribute_type}', parse_value(value, attribute.attribute_type))
                asset_attr.save()

def parse_value(value, type):
    parsers = {
        'text': lambda x: x,
        'number': lambda x: float(x) if x else None,
        'date': lambda x: x,  # Дата должна уже прийти в правильном формате
        'boolean': lambda x: bool(int(x)) if x else None,
        'email': lambda x: x,
        'url': lambda x: x,
        'json': lambda x: {},  # Сериализацию нужно реализовать отдельно
        'asset_ref': lambda x: None,  # Настройка по требованиям
        'attr_ref': lambda x: None  # Настройка по требованиям
    }
    return parsers[type](value)

def delete_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    asset.delete()
    return redirect('asset_list')
def get_attributes_by_asset_type(request, asset_type_id):
    attributes = list(AssetTypeAttribute.objects.filter(asset_type_id=asset_type_id).values('id', 'attribute__name', 'attribute__attribute_type'))
    return JsonResponse(attributes, safe=False)
def asset_list(request):
    assets = Asset.objects.prefetch_related('components', 'asset_attributes').all()
    return render(request, 'assets/asset_list.html', {'assets': assets})
def get_attributes_by_asset(request, asset_id):
    attributes = AssetAttribute.objects.filter(asset_id=asset_id).select_related('attribute')
    data = [{
        'id': attr.id,
        'attribute_name': attr.attribute.name,
        'attribute_type': attr.attribute.attribute_type,
        'value': attr.value_text  # или другое поле в зависимости от типа атрибута
    } for attr in attributes]
    return JsonResponse(data, safe=False)
