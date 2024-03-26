from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from service.forms.Asset_Forms import AssetForm
from service.models import AssetAttribute, Attribute, Asset

# Создание актива
def create_asset(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save()
            # Динамическое создание атрибутов актива после сохранения
            attributes = request.POST.getlist('attributes')
            for attribute_id in attributes:
                attribute_value = request.POST.get(f'attribute_{attribute_id}_value', '')
                attribute = Attribute.objects.get(id=attribute_id)
                AssetAttribute.objects.create(asset=asset, attribute=attribute, value=attribute_value)
            return redirect('assets_list')  # Перенаправление на список активов
    else:
        form = AssetForm()
    return render(request, 'assets/create_asset.html', {'form': form})


# Редактирование актива
def edit_asset(request, pk):
    asset = Asset.objects.get(pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            # Обновление динамических атрибутов
            AssetAttribute.objects.filter(asset=asset).delete()  # Удаление существующих атрибутов для пересоздания
            attributes = request.POST.getlist('attributes')
            for attribute_id in attributes:
                attribute_value = request.POST.get(f'attribute_{attribute_id}_value', '')
                attribute = Attribute.objects.get(id=attribute_id)
                AssetAttribute.objects.create(asset=asset, attribute=attribute, value=attribute_value)
            return redirect('assets')
    else:
        form = AssetForm(instance=asset)
    return render(request, 'assets/edit_asset.html', {'form': form, 'asset': asset})


# Удаление актива
def delete_asset(request, pk):
    asset = Asset.objects.get(pk=pk)
    if request.method == 'POST':
        asset.delete()
        return HttpResponseRedirect(reverse('assets'))  # Перенаправление на список активов
    return render(request, 'assets/delete_asset.html', {'asset': asset})


# Вывод списка активов
def asset_list(request):
    assets = Asset.objects.prefetch_related('components', 'asset_attributes').all()
    return render(request, 'assets/asset_list.html', {'assets': assets})