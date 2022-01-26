from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('', include('core.urls')),
    path('admin/doc/',include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), # Django-Allauth URLs

]
