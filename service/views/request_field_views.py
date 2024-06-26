from django.shortcuts import render, get_object_or_404, redirect
from service.models import FieldMeta, FieldAccess, RequestType
from service.forms.Request_forms import FieldMetaForm, FieldAccessFormSet
from django.contrib.auth.models import Group

def request_field_create(request, request_type_id):
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    roles = Group.objects.all()
    if request.method == 'POST':
        form = FieldMetaForm(request.POST)
        if form.is_valid():
            field_meta = form.save(commit=False)
            field_meta.save()
            field_meta.request_types.add(request_type)
            formset = FieldAccessFormSet(request.POST, instance=field_meta)
            if formset.is_valid():
                formset.save()
            return redirect('edit_request_type', pk=request_type_id)
    else:
        form = FieldMetaForm()
        field_meta_instance = FieldMeta()
        formset = FieldAccessFormSet(instance=field_meta_instance)
        for role in roles:
            FieldAccess.objects.get_or_create(field_meta=field_meta_instance, role=role)
        formset = FieldAccessFormSet(instance=field_meta_instance)
    return render(request, 'request_field/request_field_create.html', {'form': form, 'formset': formset, 'request_type': request_type, 'roles': roles})
def request_field_edit(request, request_type_id, pk):
    field_meta = get_object_or_404(FieldMeta, pk=pk)
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    roles = Group.objects.all()
    if request.method == 'POST':
        form = FieldMetaForm(request.POST, instance=field_meta)
        formset = FieldAccessFormSet(request.POST, instance=field_meta)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('edit_request_type', pk=request_type_id)
    else:
        form = FieldMetaForm(instance=field_meta)
        formset = FieldAccessFormSet(instance=field_meta)
        for role in roles:
            FieldAccess.objects.get_or_create(field_meta=field_meta, role=role)
        formset = FieldAccessFormSet(instance=field_meta)
    return render(request, 'request_field/request_field_edit.html', {'form': form, 'formset': formset, 'request_type': request_type, 'roles': roles})
