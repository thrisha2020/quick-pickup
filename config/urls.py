"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from django.contrib.admin.views.decorators import staff_member_required
from api.admin_views import admin_dashboard
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import never_cache

# Custom admin site with dashboard
admin.site.site_header = 'Campus Cart Administration'
admin.site.site_title = 'Campus Cart Admin'
admin.site.index_title = 'Dashboard'

urlpatterns = [
    # Home page
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    # Admin site
    path('admin/dashboard/', staff_member_required(admin_dashboard), name='admin-dashboard'),
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('api.urls')),
    
    # REST Framework authentication
    path('api-auth/', include('rest_framework.urls')),
    
    # Cart URLs
    path('cart/', include('cart.urls')),
    
    # Frontend templates
    path('', TemplateView.as_view(template_name='index.html'), name='student-portal'),
    path('shopkeeper/', TemplateView.as_view(template_name='shopkeeper_new.html'), name='shopkeeper-portal'),
    path('admin-signup/', TemplateView.as_view(template_name='registration/signup.html'), name='admin-signup'),
    path('signup/', TemplateView.as_view(template_name='registration/signup.html'), name='shopkeeper_signup'),
    
    # Catch-all for frontend routes (handled by frontend router)
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]

# Serve static and media files in development
if settings.DEBUG:
    # Serve static files
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', never_cache(serve), {
            'document_root': settings.STATIC_ROOT,
        }),
    ]
    # Serve media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
