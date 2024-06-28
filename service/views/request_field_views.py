from django.shortcuts import render, get_object_or_404, redirect
from service.models import FieldMeta, FieldAccess, RequestType
from service.forms.Field_forms import FieldMetaForm, FieldAccessFormSet
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
    roles = Group.objects.all()
    if request.method == 'POST':
        form = FieldMetaForm(request.POST)
        if form.is_valid():
            field_meta = form.save(commit=False)
            field_meta.save()
            request_type.field_set.fields.add(field_meta)

            formset = FieldAccessFormSet(request.POST, instance=field_meta)
            if formset.is_valid():
                formset.save()
                return redirect(reverse('edit_request_type', kwargs={'pk': request_type_id}))
    else:
        form = FieldMetaForm()
        field_meta_instance = FieldMeta()
        formset = FieldAccessFormSet(instance=field_meta_instance, queryset=FieldAccess.objects.none())

    return render(request, 'request_field/request_field_create.html', {
        'form': form,
        'formset': formset,
        'request_type': request_type,
        'roles': roles
    })
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

    return render(request, 'request_field/request_field_edit.html', {'form': form, 'formset': formset, 'request_type': request_type, 'roles': roles})
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
