from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from service.forms.Asset_Forms import AttributeForm
from service.models import Attribute, AssetType, AssetAttribute, AssetTypeAttribute


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
            # или вам может потребоваться перенаправить на другой URL в зависимости от вашей логики приложения
            return redirect('asset_type_list')
    else:
        form = AttributeForm(instance=attribute)
    return render(request, 'attributes/attribute_edit.html', {'form': form})

# Удаление атрибута
# views.py
def attribute_delete(request, pk):
    attribute = get_object_or_404(Attribute, pk=pk)
    asset_type_id = attribute.asset_types.first().id if attribute.asset_types.exists() else None
    if request.method == 'POST':
        attribute.delete()
        if asset_type_id:
            return redirect('asset_type_edit', pk=asset_type_id)
        else:
            return redirect('asset_type_list')
    # Если это GET-запрос, то предоставляем страницу с подтверждением удаления
    context = {
        'attribute': attribute,
        'asset_type_id': asset_type_id,
    }
    return render(request, 'attributes/attribute_delete.html', context)
