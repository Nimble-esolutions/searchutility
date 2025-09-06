from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.urls import reverse

# Custom admin site to redirect to custom login
class CustomAdminSite(admin.AdminSite):
    def login(self, request, extra_context=None):
        # Redirect to custom login page
        return redirect('login')
    
    def index(self, request, extra_context=None):
        # Redirect to custom login if not authenticated
        if not request.user.is_authenticated:
            return redirect('login')
        return super().index(request, extra_context)

# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')

# Register your models here.
