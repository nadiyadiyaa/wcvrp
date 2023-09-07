from django.contrib import admin
from django.urls import path
from django.conf.urls import include, handler404

urlpatterns = [
    path('', include('master.urls')),
    path('', include('transaction.urls')),
    path('admin/', admin.site.urls),
]
