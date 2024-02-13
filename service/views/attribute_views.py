from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from service.forms.Asset_Forms import AttributeForm
from service.models import Attribute, AssetType


def attribute_create(request, asset_type_id):
    asset_type = get_object_or_404(AssetType, pk=asset_type_id)
    if request.method == 'POST':
        form = AttributeForm(request.POST)
        if form.is_valid():
            attribute = form.save(commit=False)
            attribute.save()
            asset_type.attributes.add(attribute)
            return redirect('asset_type_attributes', asset_type_id=asset_type.pk)
    else:
        form = AttributeForm()
    return render(request, 'attributes/attribute_create.html', {'form': form, 'asset_type': asset_type})

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
def attribute_delete(request, pk):
    attribute = get_object_or_404(Attribute, pk=pk)
    if request.method == 'POST':
        attribute.delete()
        # Аналогично, предполагаем перенаправление на список типов активов
        # или другую страницу в зависимости от логики приложения
        return redirect('asset_type_list')
    return render(request, 'attributes/attribute_delete.html', {'object': attribute})

