from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from rest_framework.schemas import get_schema_view
from rest_framework.authtoken.views import obtain_auth_token
#from drf_yasg.views import get_schema_view as yasg_get_schema_view
#from drf_yasg import openapi

'''
schema_view = yasg_get_schema_view(
   openapi.Info(
      title="Multi-party event scheduling API",
      default_version="v1",
      description="foo",
      terms_of_service="",
      contact=openapi.Contact(email="hello@example.com"),
      license=openapi.License(name="GPL v3 License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
'''

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('schedul.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token),
    #path('dj-rest-auth/', include('dj_rest_auth.urls')),
    #path('dj-rest-auth/registration/',
    #      include('dj_rest_auth.registration.urls')),

    path('openapi', get_schema_view(
        title="_",
        description="...",
        version="0.0.1"
    ), name='openapi-schema'),

    # X: 
    #path('swagger/', schema_view.with_ui(
    #  'swagger', cache_timeout=0), name='schema-swagger-ui'),
    #path('redoc/', schema_view.with_ui(
    #  'redoc', cache_timeout=0), name='schema-redoc'),
]

import os
if os.environ.get('DJANGO_SERVE_STATIC'):
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()

'''
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('posts.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
    path('api/v1/dj-rest-auth/registration/',
          include('dj_rest_auth.registration.urls')),
    path('swagger/', schema_view.with_ui(
      'swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui(
      'redoc', cache_timeout=0), name='schema-redoc'),
]
'''
