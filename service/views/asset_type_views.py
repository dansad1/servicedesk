from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from service.models import AssetType, Attribute, AssetTypeAttribute
from service.forms.Asset_Forms import AssetTypeForm, AttributeForm


def asset_type_create(request):
    if request.method == 'POST':
        form = AssetTypeForm(request.POST)
        if form.is_valid():
            # Сохраняем новый тип актива
            asset_type = form.save()

            # Если есть родительский тип, наследуем атрибуты
            if asset_type.parent:
                parent_type = asset_type.parent

                # Переносим атрибуты от родительского типа
                parent_attributes = AssetTypeAttribute.objects.filter(asset_type=parent_type)
                for parent_attribute in parent_attributes:
                    AssetTypeAttribute.objects.create(
                        asset_type=asset_type,
                        attribute=parent_attribute.attribute
                    )

            # Перенаправляем на редактирование только что созданного типа актива
            return redirect('asset_type_edit', asset_type_id=asset_type.id)
    else:
        form = AssetTypeForm()

    return render(request, 'asset_types/asset_type_create.html', {'form': form})


def asset_type_list(request):
    asset_types = AssetType.objects.all()
    return render(request, 'asset_types/asset_type_list.html', {'asset_types': asset_types})


def asset_type_edit(request, asset_type_id):
    asset_type = get_object_or_404(AssetType, id=asset_type_id)
    type_attributes = AssetTypeAttribute.objects.filter(asset_type=asset_type)

    if request.method == 'POST':
        form = AssetTypeForm(request.POST, instance=asset_type)

        if form.is_valid():
            form.save()

            # Логика для добавления новых атрибутов
            attribute_form = AttributeForm(request.POST)
            if attribute_form.is_valid():
                new_attribute = attribute_form.save()
                AssetTypeAttribute.objects.create(asset_type=asset_type, attribute=new_attribute)

            return redirect('asset_type_edit', asset_type_id=asset_type.id)

    else:
        form = AssetTypeForm(instance=asset_type)
        attribute_form = AttributeForm()

    return render(request, 'asset_types/asset_type_edit.html', {
        'form': form,
        'attribute_form': attribute_form,
        'type_attributes': type_attributes,
        'asset_type': asset_type,
    })
@login_required
def asset_type_delete(request):
    if request.method == 'POST':
        asset_type_ids = request.POST.getlist('selected_asset_types')
        if asset_type_ids:
            AssetType.objects.filter(id__in=asset_type_ids).delete()
            messages.success(request, 'Выбранные типы активов были удалены.')
        else:
            messages.warning(request, 'Пожалуйста, выберите хотя бы один тип актива для удаления.')
    return redirect('asset_type_list')
