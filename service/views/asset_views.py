from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from service.forms.Asset_Forms import AssetForm
from service.models import AssetAttribute, Attribute, Asset, AssetTypeAttribute


# Создание актива
def create_asset(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            # Сохраняем актив и возвращаем созданный объект
            asset = form.save()

            # Итерация по динамически добавленным полям атрибутов
            for attribute in Attribute.objects.all():
                field_name = f'attribute_{attribute.pk}_value'
                if field_name in request.POST:
                    attribute_value = request.POST.get(field_name, '')
                    # Создаем и связываем AssetAttribute, только если предоставлено значение
                    if attribute_value:
                        AssetAttribute.objects.create(
                            asset=asset,
                            attribute=attribute,
                            value_text=attribute_value  # Предполагается текстовое значение, настройте в зависимости от типа атрибута
                        )

            # Перенаправление на страницу списка активов после сохранения актива и его атрибутов
            return redirect('assets_list')
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
            # We handle dynamic attribute fields, assuming they exist in the form
            for attribute in Attribute.objects.all():
                field_name = f'attribute_{attribute.pk}_value'
                if field_name in request.POST:
                    attribute_value = request.POST.get(field_name, '')
                    # Retrieve or create the AssetAttribute instance
                    asset_attr, created = AssetAttribute.objects.get_or_create(
                        asset=asset,
                        attribute=attribute,
                        defaults={'value_text': attribute_value}  # or use appropriate field based on type
                    )
                    if not created:
                        # If the instance was not created, we update the existing one
                        if attribute.attribute_type == Attribute.TEXT:
                            asset_attr.value_text = attribute_value
                        # Add other types handling here
                        asset_attr.save()

            return redirect('assets_list')  # Redirect to the asset list after updating
    else:
        form = AssetForm(instance=asset)

    return render(request, 'assets/edit_asset.html', {
        'form': form,
        'asset': asset
    })

# Функция удаления актива
def delete_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    asset.delete()
    return redirect("assets_list")

# Функция вывода списка активов
def asset_list(request):
    assets = Asset.objects.prefetch_related('components', 'asset_attributes').all()
    return render(request, 'assets/asset_list.html', {'assets': assets})

def get_attributes_by_asset_type(request, asset_type_id):
    attributes = list(AssetTypeAttribute.objects.filter(asset_type_id=asset_type_id).values('id', 'attribute__name', 'attribute__attribute_type'))
    return JsonResponse(attributes, safe=False)