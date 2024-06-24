from service.forms.Performer_forms import *
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
            group.save()
            members_ids = request.POST.get('selected_users', '').split()
            companies_ids = request.POST.get('selected_companies', '').split()
            group.members.set(members_ids)
            group.companies.set(companies_ids)
            return redirect('performer_group_list')
    else:
        form = PerformerGroupForm()
    custom_users = CustomUser.objects.all()
    companies = Company.objects.all()
    selected_member_ids = request.POST.get('selected_users', '').split()
    selected_company_ids = request.POST.get('selected_companies', '').split()
    return render(request, 'performer_group/performer_group_create.html', {
        'form': form,
        'custom_users': custom_users,
        'companies': companies,
        'selected_member_ids': selected_member_ids,
        'selected_company_ids': selected_company_ids
    })

def performer_group_update(request, pk):
    group = get_object_or_404(PerformerGroup, pk=pk)
    if request.method == 'POST':
        form = PerformerGroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            members_ids = request.POST.get('selected_users', '').split()
            companies_ids = request.POST.get('selected_companies', '').split()
            group.members.set(members_ids)
            group.companies.set(companies_ids)
            return redirect('performer_group_list')
    else:
        form = PerformerGroupForm(instance=group)
    custom_users = CustomUser.objects.all()
    companies = Company.objects.all()
    selected_member_ids = request.POST.get('selected_users', '') or group.members.values_list('id', flat=True)
    selected_company_ids = request.POST.get('selected_companies', '') or group.companies.values_list('id', flat=True)
    return render(request, 'performer_group/performer_group_update.html', {
        'form': form,
        'group': group,
        'custom_users': custom_users,
        'companies': companies,
        'selected_member_ids': selected_member_ids,
        'selected_company_ids': selected_company_ids
    })

def performer_group_delete(request, pk):
    group = get_object_or_404(PerformerGroup, pk=pk)
    group.delete()
    return redirect('performer_group/performer_group_list')