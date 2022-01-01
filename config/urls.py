from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('schedul.urls')),
    path('api-foo/', include('rest_framework.urls')),
]
