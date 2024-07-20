from django.shortcuts import render, get_object_or_404, redirect
from service.models import FieldMeta, FieldAccess, RequestType
from service.forms.Field_forms import FieldMetaForm, FieldAccessForm
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.urls import reverse


def get_default_value_widget(request):
    field_type = request.GET.get('field_type')
    form = FieldMetaForm()
    widget = form.get_default_value_field(field_type)
    widget_html = widget.widget.render('default_value', None, attrs={'class': 'form-control'})
    return JsonResponse({'widget': widget_html})

def save_field_access(field_meta, groups, request):
    for group in groups:
        can_read = request.POST.get(f'can_read_{group.id}') == 'on'
        can_update = request.POST.get(f'can_update_{group.id}') == 'on'
        access, created = FieldAccess.objects.get_or_create(field_meta=field_meta, role=group)
        access.can_read = can_read
        access.can_update = can_update
        access.save()

def request_field_create(request, request_type_id):
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    groups = Group.objects.all()
    if request.method == 'POST':
        form = FieldMetaForm(request.POST)
        if form.is_valid():
            field_meta = form.save(commit=False)
            field_meta.save()
            request_type.field_set.fields.add(field_meta)
            save_field_access(field_meta, groups, request)
            return redirect('edit_request_type', request_type_id=request_type_id)
    else:
        form = FieldMetaForm()

    return render(request, 'request_field/request_field_create.html', {
        'form': form,
        'request_type': request_type,
        'groups': groups,
    })

def request_field_edit(request, request_type_id, pk):
    field_meta = get_object_or_404(FieldMeta, pk=pk)
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    groups = Group.objects.all()
    group_permissions = [
        {
            'group': group,
            'can_read': FieldAccess.objects.filter(field_meta=field_meta, role=group, can_read=True).exists(),
            'can_update': FieldAccess.objects.filter(field_meta=field_meta, role=group, can_update=True).exists(),
        }
        for group in groups
    ]

    if request.method == 'POST':
        form = FieldMetaForm(request.POST, instance=field_meta)
        if form.is_valid():
            form.save()
            save_field_access(field_meta, groups, request)
            return redirect(reverse('edit_request_type', kwargs={'pk': request_type_id}))
    else:
        form = FieldMetaForm(instance=field_meta)

    return render(request, 'request_field/request_field_edit.html', {
        'form': form,
        'request_type': request_type,
        'group_permissions': group_permissions,
    })
def request_field_list(request, request_type_id):
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    fields = request_type.field_set.fields.all()
    return render(request, 'settings/request_type.html', {
        'fields': fields,
        'request_type': request_type
    })

def request_field_delete(request, request_type_id, pk):
    field_meta = get_object_or_404(FieldMeta, pk=pk)
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    if request.method == 'POST':
        request_type.field_set.fields.remove(field_meta)
        field_meta.delete()
        return redirect(reverse('edit_request_type', kwargs={'pk': request_type_id}))
    return redirect(reverse('edit_request_type', kwargs={'pk': request_type_id}))