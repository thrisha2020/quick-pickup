from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages

class StudentPortalView(TemplateView):
    template_name = 'student_portal.html'

class ShopkeeperPortalView(LoginRequiredMixin, TemplateView):
    template_name = 'shopkeeper_portal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data for the shopkeeper portal
        return context


class AdminSignupView(TemplateView):
    template_name = 'registration/admin_signup.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data for the admin signup page
        return context
