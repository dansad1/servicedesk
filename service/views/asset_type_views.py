from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from service.models import AssetType, Attribute
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
    if request.method == 'POST':
        form = AssetTypeForm(request.POST, instance=asset_type)
        if form.is_valid():
            form.save()
            return redirect('asset_type_list')
    else:
        form = AssetTypeForm(instance=asset_type)
    # Передаем asset_type в контекст
    return render(request, 'asset_types/asset_type_edit.html', {'form': form, 'asset_type': asset_type})
def asset_type_delete(request, pk):
    asset_type = AssetType.objects.get(pk=pk)
    asset_type.delete()
    return redirect('asset_type_list')
