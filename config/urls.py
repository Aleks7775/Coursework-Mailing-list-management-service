from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('messagin_service.urls', namespace='messagin_service'))
]
