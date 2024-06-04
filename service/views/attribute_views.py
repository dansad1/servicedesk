from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from service.forms.Asset_Forms import AttributeForm
from service.models import Attribute, AssetType, AssetAttribute, AssetTypeAttribute
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# Создание атрибута
def attribute_create(request, asset_type_id):
    asset_type = get_object_or_404(AssetType, pk=asset_type_id)
    if request.method == 'POST':
        form = AttributeForm(request.POST)
        if form.is_valid():
            attribute = form.save()
            # Создание связи через промежуточную модель
            AssetTypeAttribute.objects.create(asset_type=asset_type, attribute=attribute)
            return redirect('asset_type_edit', pk=asset_type.pk)
    else:
        form = AttributeForm()
    return render(request, 'attributes/attribute_create.html', {'form': form, 'asset_type': asset_type})


# Редактирование атрибута
def attribute_edit(request, pk):
    attribute = get_object_or_404(Attribute, pk=pk)
    if request.method == 'POST':
        form = AttributeForm(request.POST, instance=attribute)
        if form.is_valid():
            form.save()
            # Предполагаем, что есть URL с именем 'asset_type_list' для перенаправления
            return redirect('asset_type_list')
    else:
        form = AttributeForm(instance=attribute)
    return render(request, 'attributes/attribute_edit.html', {'form': form, 'attribute': attribute})

# Удаление атрибута
@require_POST
def attribute_delete_from_type(request, pk, asset_type_id):
    AssetTypeAttribute.objects.filter(asset_type_id=asset_type_id, attribute_id=pk).delete()
    return JsonResponse({'status': 'success'})
@require_POST
def attribute_delete_from_asset(request, pk, asset_id):
    AssetAttribute.objects.filter(asset_id=asset_id, attribute_id=pk).delete()
    return JsonResponse({'status': 'success'})
