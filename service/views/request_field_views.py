from django.shortcuts import render, get_object_or_404, redirect
from service.models import FieldMeta, FieldAccess, RequestType
from service.forms.Field_forms import FieldMetaForm
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.urls import reverse


def get_default_value_widget(request):
    field_type = request.GET.get('field_type')
    form = FieldMetaForm()
    widget = form.get_default_value_field(field_type)
    widget_html = widget.widget.render('default_value', None, attrs={'class': 'form-control'})
    return JsonResponse({'widget': widget_html})
def request_field_create(request, request_type_id):
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    if request.method == 'POST':
        form = FieldMetaForm(request.POST, request.FILES)
        if form.is_valid():
            field_meta = form.save(commit=False)
            field_meta.save()
            request_type.field_set.fields.add(field_meta)
            return redirect(reverse('request_type_edit', kwargs={'pk': request_type_id}))
    else:
        form = FieldMetaForm()

    return render(request, 'settings/request_type_form.html', {
        'form': form,
        'request_type': request_type,
        'operation': 'create'
    })

def request_field_edit(request, request_type_id, field_id):
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    field_meta = get_object_or_404(FieldMeta, pk=field_id)
    if request.method == 'POST':
        form = FieldMetaForm(request.POST, request.FILES, instance=field_meta)
        if form.is_valid():
            form.save()
            return redirect(reverse('request_type_edit', kwargs={'pk': request_type_id}))
    else:
        form = FieldMetaForm(instance=field_meta)

    return render(request, 'settings/request_type_form.html', {
        'form': form,
        'request_type': request_type,
        'field_meta': field_meta,
        'operation': 'edit'
    })

def request_field_access_update(request, request_type_id, field_id):
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    field_meta = get_object_or_404(FieldMeta, pk=field_id)
    roles = Group.objects.all()

    if request.method == 'POST':
        for role in roles:
            can_read = request.POST.get(f'can_read_{role.id}', 'off') == 'on'
            can_update = request.POST.get(f'can_update_{role.id}', 'off') == 'on'
            FieldAccess.objects.update_or_create(
                role=role, field_meta=field_meta,
                defaults={'can_read': can_read, 'can_update': can_update}
            )
        return redirect(reverse('request_type_edit', kwargs={'pk': request_type_id}))

    read_roles = FieldAccess.objects.filter(field_meta=field_meta, can_read=True).values_list('role_id', flat=True)
    update_roles = FieldAccess.objects.filter(field_meta=field_meta, can_update=True).values_list('role_id', flat=True)

    return render(request, 'settings/request_type_form.html', {
        'request_type': request_type,
        'field_meta': field_meta,
        'roles': roles,
        'read_roles': read_roles,
        'update_roles': update_roles,
        'operation': 'access'
    })

def request_field_list(request, request_type_id):
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    fields = request_type.field_set.fields.all()
    return render(request, 'settings/request_type.html', {'fields': fields, 'request_type': request_type})


def request_field_delete(request, request_type_id, pk):
    field_meta = get_object_or_404(FieldMeta, pk=pk)
    request_type = get_object_or_404(RequestType, pk=request_type_id)

    if request.method == 'POST':
        request_type.field_set.fields.remove(field_meta)
        field_meta.delete()
        return redirect(reverse('edit_request_type', kwargs={'pk': request_type_id}))

    return redirect(reverse('edit_request_type', kwargs={'pk': request_type_id}))
