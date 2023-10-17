from django.shortcuts import render, redirect
from service.forms import CompanyForm
from django.urls import reverse_lazy
from service.models import CustomUser, Company, Request, Status
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from ..permissions import can_create_company

