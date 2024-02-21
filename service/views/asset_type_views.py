from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from service.models import AssetType
from service.forms.Asset_Forms import AssetTypeForm  # Предполагается, что у вас есть форма для модели AssetType

# Создание типа актива
def create_asset_type(request):
    if request.method == 'POST':
        form = AssetTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('asset_type_list')  # URL к списку типов активов
    else:
        form = AssetTypeForm()
    return render(request, 'asset_types/asset_type_create.html', {'form': form})


# Редактирование типа актива
def edit_asset_type(request, pk):
    asset_type = AssetType.objects.get(pk=pk)
    if request.method == 'POST':
        form = AssetTypeForm(request.POST, instance=asset_type)
        if form.is_valid():
            form.save()
            return redirect('asset_type_list')  # Обновлено для перенаправления на список типов активов
    else:
        form = AssetTypeForm(instance=asset_type)
    return render(request, 'asset_types/asset_type_edit.html', {'form': form})


# Вывод списка типов актива
def asset_type_list(request):
    asset_types = AssetType.objects.all()
    return render(request, 'asset_types/asset_type_list.html', {'asset_types': asset_types})


# Удаление типа актива
def asset_type_delete(request, pk):
    if request.method == 'POST':
        asset_type = get_object_or_404(AssetType, pk=pk)
        asset_type.delete()
    return redirect('asset_type_list')