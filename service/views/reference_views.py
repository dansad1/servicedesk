from django.shortcuts import render, get_object_or_404, redirect
from service.models import Reference, ReferenceItem
from service.forms.ReferenceForms import ReferenceForm, ReferenceItemForm
from django.contrib import messages

def reference_list(request):
    """
    Представление для отображения всех справочников.
    """
    references = Reference.objects.all()
    context = {'references': references, 'title': 'Справочники'}
    return render(request, 'references/reference_list.html', context)

def reference_create(request):
    """
    Представление для создания нового справочника.
    """
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reference_list')
    else:
        form = ReferenceForm()
    context = {'form': form, 'title': 'Создать справочник'}
    return render(request, 'references/reference_create.html', context)


def reference_edit(request, reference_id):
    reference = get_object_or_404(Reference, id=reference_id)
    items = ReferenceItem.objects.filter(reference=reference)  # Получаем все элементы для данного справочника

    if request.method == 'POST':
        form = ReferenceForm(request.POST, instance=reference)
        if form.is_valid():
            form.save()
            return redirect('reference_list')
    else:
        form = ReferenceForm(instance=reference)

    context = {
        'form': form,
        'reference': reference,
        'items': items,  # Передаем элементы в контекст
        'title': f'Редактирование справочника: {reference.name}',
    }
    return render(request, 'references/reference_edit.html', context)

def reference_delete(request, reference_id):
    """
    Представление для удаления справочника.
    """
    reference = get_object_or_404(Reference, id=reference_id)
    reference.delete()
    return redirect('reference_list')



def reference_item_create(request, reference_id):
    """
    Представление для создания нового элемента справочника.
    """
    reference = get_object_or_404(Reference, id=reference_id)
    if request.method == 'POST':
        form = ReferenceItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.reference = reference
            item.save()
            return redirect('reference_edit', reference_id=reference.id)
    else:
        form = ReferenceItemForm()
    context = {'form': form, 'reference': reference, 'title': 'Добавить элемент справочника'}
    return render(request, 'references/reference_item_create.html', context)

def reference_item_edit(request, item_id):
    """
    Представление для редактирования элемента справочника.
    """
    item = get_object_or_404(ReferenceItem, id=item_id)
    reference = item.reference
    if request.method == 'POST':
        form = ReferenceItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('reference_edit', reference_id=reference.id)
    else:
        form = ReferenceItemForm(instance=item)
    context = {'form': form, 'reference': reference, 'title': 'Редактировать элемент справочника'}
    return render(request, 'references/reference_item_edit.html', context)

def reference_item_delete(request, item_id):
    """
    Представление для удаления элемента справочника.
    """
    item = get_object_or_404(ReferenceItem, id=item_id)
    reference_id = item.reference.id
    item.delete()
    return redirect('reference_edit', reference_id=reference_id)
