from django.urls import path
from schedul.views import EventList, EventDetail, DispatchLog, EventNotify

urlpatterns = [
    path('', EventList.as_view(), name='event-list'),
    path('<int:pk>/', EventDetail.as_view(), name='event-detail'),

    path('<int:pk>/log/', DispatchLog.as_view(), name='dispatch-log'),
    path('<int:pk>/notify/', EventNotify.as_view(), name='event-notify'),

]
