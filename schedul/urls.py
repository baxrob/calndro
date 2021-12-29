from django.urls import path
from schedul.views import EventList, EventDetail

urlpatterns = [
    path('', EventList.as_view(), name='event-list'),
    path('<int:pk>/', EventDetail.as_view(), name='event-detail'),
]
'''
    path('/', EventList.as_view()),
    path('/<int:pk>/', EventDetail.as_view()),
    path('/<int:pk>/narrow/', EventUpdate.as_view()),

    path('/', Events.as_view()),
    path('/<int:pk>/', Event.as_view()),
    path('/<int:pk>/narrow/', Event.as_view()),

    path('/', EventListCreate.as_view()),
    path('/<int:pk>/', EventDetail.as_view()),
    path('/<int:pk>/narrow/', EventDetail.as_view()),
'''
