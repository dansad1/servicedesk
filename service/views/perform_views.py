from service.forms import PerformerGroupForm
from service.models import PerformerGroup, Company, CustomUser
from django.shortcuts import render, redirect, get_object_or_404

def performer_group_list(request):
    # Используйте prefetch_related для оптимизации запросов к отношениям многие-ко-многим
    groups = PerformerGroup.objects.prefetch_related('companies').all()
    return render(request, 'performer_group/performer_group_list.html', {'groups': groups})


def performer_group_create(request):
    if request.method == 'POST':
        form = PerformerGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            # Manually process 'members' and 'companies' fields
            selected_members = request.POST.getlist('selected_members')  # Names of your checkboxes
            selected_companies = request.POST.getlist('selected_companies')
            group.save()
            group.members.set(selected_members)
            group.companies.set(selected_companies)
            return redirect('performer_group_list')
    else:
        form = PerformerGroupForm()

    custom_users = CustomUser.objects.all()
    companies = Company.objects.all()
    context = {
        'form': form,
        'custom_users': custom_users,
        'companies': companies
    }
    return render(request, 'performer_group/performer_group_create.html', context)


def performer_group_update(request, pk):
    group = get_object_or_404(PerformerGroup, pk=pk)
    if request.method == 'POST':
        form = PerformerGroupForm(request.POST, instance=group)
        if form.is_valid():
            # Сохраняем изменения без коммита в базу данных
            updated_group = form.save(commit=False)
            updated_group.save()  # Сохраняем объект группы

            # Обработка выбранных пользователей
            selected_members = request.POST.getlist('selected_members')  # Имена ваших чекбоксов
            selected_companies = request.POST.getlist('selected_companies')  # Имена ваших чекбоксов
            # Устанавливаем выбранных пользователей и компании
            updated_group.members.set(selected_members)
            updated_group.companies.set(selected_companies)
            # Перенаправляем на страницу со списком групп
            return redirect('performer_group_list')
    else:
        form = PerformerGroupForm(instance=group)

    custom_users = CustomUser.objects.all()
    companies = Company.objects.all()
    context = {
        'form': form,
        'group': group,
        'custom_users': custom_users,
        'companies': companies
    }
    return render(request, 'performer_group/performer_group_update.html', context)


def performer_group_delete(request, pk):
    group = get_object_or_404(PerformerGroup, pk=pk)
    group.delete()
    return redirect('performer_group/performer_group_list')