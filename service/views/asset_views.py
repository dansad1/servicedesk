from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from service.forms.Asset_Forms import AssetForm
from service.models import AssetAttribute, Attribute, Asset

# Создание актива
def create_asset(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save()
            attributes = request.POST.getlist('attributes')
            for attribute_id in attributes:
                attribute_value = request.POST.get(f'attribute_{attribute_id}_value', '')
                attribute = Attribute.objects.get(id=attribute_id)
                AssetAttribute.objects.create(asset=asset, attribute=attribute, value=attribute_value)
            return redirect('assets_list')  # Перенаправление на список активов
    else:
        form = AssetForm()
    return render(request, 'assets/create_asset.html', {'form': form})

# Функция редактирования актива
def edit_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            # Удаляем старые атрибуты только если есть изменения
            current_attribute_ids = [str(attr.attribute.id) for attr in AssetAttribute.objects.filter(asset=asset)]
            new_attribute_ids = request.POST.getlist('attributes')
            if set(current_attribute_ids) != set(new_attribute_ids):
                AssetAttribute.objects.filter(asset=asset).delete()
                for attribute_id in new_attribute_ids:
                    attribute_value = request.POST.get(f'attribute_{attribute_id}_value', '')
                    attribute = Attribute.objects.get(id=attribute_id)
                    AssetAttribute.objects.create(asset=asset, attribute=attribute, value=attribute_value)
            return redirect('assets_list')
    else:
        form = AssetForm(instance=asset)
    return render(request, 'assets/edit_asset.html', {'form': form, 'asset': asset})


# Функция удаления актива
def delete_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        return HttpResponseRedirect(reverse('assets'))  # Перенаправление на список активов
    return render(request, 'assets/delete_asset.html', {'asset': asset})

# Функция вывода списка активов
def asset_list(request):
    assets = Asset.objects.prefetch_related('components', 'asset_attributes').all()
    return render(request, 'assets/asset_list.html', {'assets': assets})