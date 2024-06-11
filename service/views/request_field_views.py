from django.shortcuts import render, get_object_or_404, redirect
from .models import FieldMeta, FieldAccess, RequestType
from .forms import FieldMetaForm, FieldAccessFormSet

def request_type_detail(request, pk):
    request_type = get_object_or_404(RequestType, pk=pk)
    fields = FieldMeta.objects.filter(request_type=request_type)
    return render(request, 'request_type_detail.html', {'request_type': request_type, 'fields': fields})

def field_meta_create(request, request_type_id):
    request_type = get_object_or_404(RequestType, pk=request_type_id)
    if request.method == 'POST':
        form = FieldMetaForm(request.POST)
        if form.is_valid():
            field_meta = form.save(commit=False)
            field_meta.request_type = request_type
            field_meta.save()
            formset = FieldAccessFormSet(request.POST, instance=field_meta)
            if formset.is_valid():
                formset.save()
            return redirect('request_type_detail', pk=request_type_id)
    else:
        form = FieldMetaForm()
        formset = FieldAccessFormSet(instance=FieldMeta())
    return render(request, 'field_meta_form.html', {'form': form, 'formset': formset, 'request_type': request_type})

def field_meta_edit(request, request_type_id, pk):
    field_meta = get_object_or_404(FieldMeta, pk=pk, request_type_id=request_type_id)
    if request.method == 'POST':
        form = FieldMetaForm(request.POST, instance=field_meta)
        formset = FieldAccessFormSet(request.POST, instance=field_meta)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('request_type_edit', pk=request_type_id)
    else:
        form = FieldMetaForm(instance=field_meta)
        formset = FieldAccessFormSet(instance=field_meta)
    return render(request, 'field_meta_form.html', {'form': form, 'formset': formset, 'request_type': field_meta.request_type})
