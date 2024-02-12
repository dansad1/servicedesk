# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from service.forms.Settings_forms import RequestTypeForm, PriorityForm, PriorityDurationForm, StatusForm, StatusTransitionForm
from ..models import RequestType, Priority, PriorityDuration, Status, StatusTransition

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required



def create_or_edit_request_type(request, pk=None):
    if pk:
        request_type = get_object_or_404(RequestType, pk=pk)
        form = RequestTypeForm(request.POST or None, instance=request_type)
    else:
        request_type = None
        form = RequestTypeForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Тип заявки успешно сохранен.")
            return redirect('types_list')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")

    context = {
        'form': form,
        'request_type': request_type
    }
    return render(request, 'settings/request_type.html', context)
def types_list(request):
    request_types = RequestType.objects.all()
    return render(request, 'settings/types_list.html', {'request_types': request_types})
@login_required
@require_POST
def delete_request_type(request, pk):
    request_type = get_object_or_404(RequestType, pk=pk)
    request_type.delete()
    messages.success(request, "Тип заявки успешно удален.")
    return redirect('types_list')
def create_or_edit_priority(request, pk=None):
    if pk:
        priority = get_object_or_404(Priority, pk=pk)
        form = PriorityForm(request.POST or None, instance=priority)
    else:
        priority = None
        form = PriorityForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Приоритет успешно сохранен.")
        return redirect('priority_list')

    context = {
        'form': form,
        'priority': priority
    }
    return render(request, 'settings/priority.html', context)

def priority_list(request):
    priorities = Priority.objects.all().order_by('name')
    return render(request, 'settings/priority_list.html', {'priorities': priorities})
@login_required
@require_POST
def delete_priority(request, pk):
    priority = get_object_or_404(Priority, pk=pk)
    priority.delete()
    messages.success(request, "Приоритет успешно удален.")
    return redirect('priority_list')
def priority_duration_list(request):
    durations = PriorityDuration.objects.all()
    return render(request, 'settings/priority_duration_list.html', {'durations': durations})

def create_or_edit_priority_duration(request, pk=None):
    if pk:
        duration = get_object_or_404(PriorityDuration, pk=pk)
        form = PriorityDurationForm(request.POST or None, instance=duration)
    else:
        form = PriorityDurationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Продолжительность приоритета успешно сохранена.")
        return redirect('priority_duration_list')

    context = {
        'form': form
    }
    return render(request, 'settings/priority_duration.html', context)
def status_list(request):
    statuses = Status.objects.all()
    return render(request, 'settings/status_list.html', {'statuses': statuses})

# Create and edit view for statuses
def create_or_edit_status(request, pk=None):
    if pk:
        status = get_object_or_404(Status, pk=pk)
        form = StatusForm(request.POST or None, instance=status)
    else:
        form = StatusForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('status_list')

    context = {'form': form}
    return render(request, 'settings/status_create.html', context)
@login_required
@require_POST  # Убедитесь, что запрос на удаление выполняется через POST
def delete_status(request, pk):
    status = get_object_or_404(Status, pk=pk)
    status.delete()
    messages.success(request, "Статус успешно удален.")
    return redirect('status_list')



@login_required
def status_transition(request):
    if request.method == 'POST':
        form = StatusTransitionForm(request.POST)
        if form.is_valid():
            # Сохраняем переход статуса без коммита, чтобы добавить группы отдельно
            transition = form.save(commit=False)
            transition.save()
            # Получаем список групп из cleaned_data
            groups = form.cleaned_data['allowed_groups']  # Используйте 'allowed_groups' здесь
            # Добавляем каждую группу к переходу
            for group in groups:
                transition.allowed_groups.add(group)  # И здесь 'allowed_groups'
            # transition.save() не нужно вызывать повторно, так как add() уже сохраняет связи
            messages.success(request, "Status transition successfully created.")
            return redirect('status_transition')
        else:
            messages.error(request, "There was an error with the form.")
    else:
        form = StatusTransitionForm()

    transitions = StatusTransition.objects.all()
    return render(request, 'settings/status_transition.html', {
        'transitions': transitions,
        'form': form
    })

def delete_status_transition(request, pk):
    transition_instance = get_object_or_404(StatusTransition, pk=pk)
    if request.method == 'POST':
        transition_instance.delete()
        messages.success(request, "Status transition successfully deleted.")
        return redirect('status_transition')

def settings_sidebar(request):
    return render(request, 'settings/settings_sidebar.html')
