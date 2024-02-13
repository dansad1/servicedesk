from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from service.models import AssetType
from service.forms.Asset_Forms import AssetTypeForm  # Предполагается, что у вас есть форма для модели AssetType

def create_asset_type(request):
    if request.method == 'POST':
        form = AssetTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('asset_type_list')  # URL к списку типов активов
    else:
        form = AssetTypeForm()
    return render(request, 'asset_types/create_asset_type.html', {'form': form})
def edit_asset_type(request, pk):
    asset_type = AssetType.objects.get(pk=pk)
    if request.method == 'POST':
        form = AssetTypeForm(request.POST, instance=asset_type)
        if form.is_valid():
            form.save()
            return redirect('asset_type_list')  # Обновлено для перенаправления на список типов активов
    else:
        form = AssetTypeForm(instance=asset_type)
    return render(request, 'asset_types/edit_asset_type.html', {'form': form})
def asset_type_list(request):
    asset_types = AssetType.objects.all()
    return render(request, 'asset_types/asset_type_list.html', {'asset_types': asset_types})
def delete_asset_type(request, pk):
    asset_type = AssetType.objects.get(pk=pk)
    if request.method == 'POST':
        asset_type.delete()
        return HttpResponseRedirect(reverse('asset_type_list'))  # URL к списку типов активов
    return render(request, 'asset_types/delete_asset_type.html', {'asset_type': asset_type})