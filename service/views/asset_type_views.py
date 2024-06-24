from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from service.models import AssetType, Attribute, AssetTypeAttribute
from service.forms.Asset_Forms import AssetTypeForm

def asset_type_create(request):
    if request.method == 'POST':
        form = AssetTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('asset_type_list')
    else:
        form = AssetTypeForm()
    return render(request, 'asset_types/asset_type_create.html', {'form': form})

def asset_type_list(request):
    asset_types = AssetType.objects.all()
    return render(request, 'asset_types/asset_type_list.html', {'asset_types': asset_types})

def asset_type_edit(request, pk):
    asset_type = get_object_or_404(AssetType, pk=pk)
    # Получение атрибутов через промежуточную модель AssetTypeAttribute
    attributes = AssetTypeAttribute.objects.filter(asset_type=asset_type).select_related('attribute')

    if request.method == 'POST':
        form = AssetTypeForm(request.POST, instance=asset_type)
        if form.is_valid():
            form.save()
            # Можно добавить сообщение об успешном сохранении
            return redirect('asset_type_list')
    else:
        form = AssetTypeForm(instance=asset_type)

    context = {
        'form': form,
        'asset_type': asset_type,
        'attributes': [attr.attribute for attr in attributes]  # Преобразование в список атрибутов
    }
    return render(request, 'asset_types/asset_type_edit.html', context)


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
