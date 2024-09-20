from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages

from service.forms.Asset_Forms import AttributeForm
from service.models import AssetType, AssetTypeAttribute, AssetAttribute, Asset, Attribute


def attribute_create_for_type(request, asset_type_id, component_type_id=None):
    """
    Функция для создания атрибута для типа актива или его компонента.
    """
    # Получаем основной тип актива
    asset_type = get_object_or_404(AssetType, pk=asset_type_id)
    component_type = None

    # Если компонент указан, получаем его
    if component_type_id:
        component_type = get_object_or_404(AssetType, pk=component_type_id)

    if request.method == 'POST':
        form = AttributeForm(request.POST)
        if form.is_valid():
            attribute = form.save()

            if component_type:
                # Привязываем атрибут к компоненту
                AssetTypeAttribute.objects.create(asset_type=component_type, attribute=attribute)
                messages.success(request, 'Атрибут успешно создан для компонента.')
                # Возвращаемся к редактированию всего актива
                return redirect('asset_type_edit', asset_type_id=asset_type_id)
            else:
                # Привязываем атрибут к основному типу
                AssetTypeAttribute.objects.create(asset_type=asset_type, attribute=attribute)
                messages.success(request, 'Атрибут успешно создан для типа актива.')
                return redirect('asset_type_edit', asset_type_id=asset_type_id)
    else:
        form = AttributeForm()

    return render(request, 'attributes/attribute_create_for_type.html', {
        'form': form,
        'asset_type': asset_type,
        'component_type': component_type
    })

def attribute_edit_for_type(request, asset_type_id, attribute_id, component_type_id=None):
    """
    Функция для редактирования атрибута, привязанного к типу актива или его компоненту.
    """
    # Получаем основной тип актива
    asset_type = get_object_or_404(AssetType, pk=asset_type_id)
    component_type = None

    # Если компонент указан, получаем его
    if component_type_id:
        component_type = get_object_or_404(AssetType, pk=component_type_id)

    attribute = get_object_or_404(Attribute, pk=attribute_id)

    if request.method == 'POST':
        form = AttributeForm(request.POST, instance=attribute)
        if form.is_valid():
            form.save()

            if component_type:
                messages.success(request, 'Атрибут успешно обновлен для компонента.')
                # Возвращаемся к редактированию всего актива
                return redirect('asset_type_edit', asset_type_id=asset_type_id)
            else:
                messages.success(request, 'Атрибут успешно обновлен для типа актива.')
                return redirect('asset_type_edit', asset_type_id=asset_type_id)
    else:
        form = AttributeForm(instance=attribute)

    return render(request, 'attributes/attribute_edit_for_type.html', {
        'form': form,
        'asset_type': asset_type,
        'component_type': component_type,
        'attribute': attribute
    })

@require_POST
def attribute_delete_from_type(request, asset_type_id, attribute_id, component_type_id=None):
    """
    Функция для удаления атрибута, связанного с типом актива или его компонентом.
    """
    asset_type = get_object_or_404(AssetType, pk=asset_type_id)

    # Если компонент указан, удаляем атрибут компонента
    if component_type_id:
        component_type = get_object_or_404(AssetType, pk=component_type_id)
        AssetTypeAttribute.objects.filter(asset_type_id=component_type.id, attribute_id=attribute_id).delete()
        messages.success(request, 'Атрибут компонента успешно удален.')
    else:
        # Удаляем атрибут основного типа актива
        AssetTypeAttribute.objects.filter(asset_type_id=asset_type.id, attribute_id=attribute_id).delete()
        messages.success(request, 'Атрибут типа актива успешно удален.')

    # Возврат на редактирование основного типа актива
    return redirect('asset_type_edit', asset_type_id=asset_type_id)


def attribute_list_for_type(request, asset_type_id):
    asset_type = get_object_or_404(AssetType, pk=asset_type_id)
    attributes = AssetTypeAttribute.objects.filter(asset_type=asset_type)

    return render(request, 'asset_types/asset_type_edit.html', {
        'asset_type': asset_type,
        'attributes': attributes
    })
def attribute_create_for_asset(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id)

    if request.method == 'POST':
        form = AttributeForm(request.POST)
        if form.is_valid():
            attribute = form.save()
            # Создаем связь между атрибутом и активом
            AssetAttribute.objects.create(asset=asset, attribute=attribute)
            return redirect('asset_edit', pk=asset_id)
    else:
        form = AttributeForm()

    return render(request, 'attributes/attribute_create_for_type.html', {'form': form, 'asset': asset})
def attribute_edit_for_asset(request, asset_id, attribute_id):
    asset = get_object_or_404(Asset, pk=asset_id)
    attribute = get_object_or_404(Attribute, pk=attribute_id)

    if request.method == 'POST':
        form = AttributeForm(request.POST, instance=attribute)
        if form.is_valid():
            form.save()
            return redirect('asset_edit', pk=asset_id)
    else:
        form = AttributeForm(instance=attribute)

    return render(request, 'attributes/attribute_edit_for_asset.html', {
        'form': form,
        'asset': asset,
        'attribute': attribute
    })


@require_POST
def attribute_delete_from_asset(request, asset_id, attribute_id):
    # Удаляем связь между активом и атрибутом
    AssetAttribute.objects.filter(asset_id=asset_id, attribute_id=attribute_id).delete()

    messages.success(request, 'Атрибут был успешно удалён.')
    return redirect('asset_edit', pk=asset_id)


def attribute_list_for_asset(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id)
    attributes = AssetAttribute.objects.filter(asset=asset)
    return render(request, 'attributes/attribute_list_for_asset.html', {
        'asset': asset,
        'attributes': attributes
    })
