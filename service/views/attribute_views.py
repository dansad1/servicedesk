from django.shortcuts import redirect, render
from service.forms.Asset_Forms import AttributeForm
def attribute_create(request):
    if request.method == 'POST':
        form = AttributeForm(request.POST)
        if form.is_valid():
            attribute = form.save()
            # Перенаправление может быть на страницу редактирования этого же атрибута
            # или на страницу списка, если такая логика предпочтительнее
            return redirect('attribute_edit.html', pk=attribute.pk)
    else:
        form = AttributeForm()
    return render(request, 'attributes/attribute_create.html', {'form': form})
