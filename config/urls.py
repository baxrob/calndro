from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('schedul.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token),

    path('openapi', get_schema_view(
        title="_",
        description="...",
        version="0.0.1"
    ), name='openapi-schema'),
]

import os
if os.environ.get('DJANGO_SERVE_STATIC'):
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()

