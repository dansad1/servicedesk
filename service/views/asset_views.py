from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from service.forms.Asset_Forms import AssetForm
from service.models import AssetAttribute, Attribute, Asset, AssetTypeAttribute
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Создание актива
def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()  # Форма обрабатывает как актив, так и атрибуты
            return redirect('asset_list')
    else:
        form = AssetForm()

    return render(request, 'assets/asset_create.html', {'form': form})
# Функция редактирования актива
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)

    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()  # Форма обрабатывает как актив, так и атрибуты
            return redirect('asset_list')
    else:
        form = AssetForm(instance=asset)

    return render(request, 'assets/asset_edit.html', {'form': form, 'asset': asset})
# Функция удаления актива
@login_required
def asset_delete(request):
    if request.method == 'POST':
        asset_ids = request.POST.getlist('selected_assets')
        if asset_ids:
            Asset.objects.filter(id__in=asset_ids).delete()
            messages.success(request, 'Выбранные активы были удалены.')
        else:
            messages.warning(request, 'Пожалуйста, выберите хотя бы один актив для удаления.')
    return redirect('asset_list')
# Функция вывода списка активов
def asset_list(request):
    assets = Asset.objects.select_related('asset_type', 'parent_asset').prefetch_related('asset_attributes__attribute').all()
    return render(request, 'assets/asset_list.html', {'assets': assets})

def get_inherited_attributes(request, asset_type_id):
    parent_asset_id = request.GET.get('parent_asset_id')

    # Список для хранения атрибутов
    attributes = []

    # Получаем атрибуты, связанные с типом актива
    if asset_type_id:
        type_attributes = AssetTypeAttribute.objects.filter(asset_type_id=asset_type_id).values('attribute__id', 'attribute__name', 'attribute__attribute_type')
        attributes.extend(list(type_attributes))

    # Если указан родительский актив, добавляем его атрибуты
    if parent_asset_id:
        parent_attributes = AssetAttribute.objects.filter(asset_id=parent_asset_id).values(
            'attribute__id', 'attribute__name', 'attribute__attribute_type',
            'value_text', 'value_number', 'value_date', 'value_boolean', 'value_email', 'value_url', 'value_json'
        )
        for attr in parent_attributes:
            attr_value = (
                attr['value_text'] or attr['value_number'] or attr['value_date'] or
                attr['value_boolean'] or attr['value_email'] or attr['value_url'] or attr['value_json']
            )
            attributes.append({
                'id': attr['attribute__id'],
                'attribute__name': attr['attribute__name'],
                'attribute__attribute_type': attr['attribute__attribute_type'],
                'value': attr_value
            })

    # Возвращаем атрибуты в формате JSON
    return JsonResponse(attributes, safe=False)