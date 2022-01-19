from django.urls import path
from schedul.views import EventList, EventDetail, DispatchLog, EventNotify

urlpatterns = [
    path('', EventList.as_view(), name='event-list'),
    path('<int:pk>/', EventDetail.as_view(), name='event-detail'),

    path('<int:pk>/log/', DispatchLog.as_view(), name='dispatch-log'),
    path('<int:pk>/notify/', EventNotify.as_view(), name='event-notify'),

    #path('dispatch/', DispatchList.as_view()),
    #path('dispatch/<int:pk>/', DispatchDetail.as_view()),
    #path('dispatch/<int:pk>/notify/', DispatchNotification.as_view()),
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
