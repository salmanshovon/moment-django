from django.urls import path
from .views import SchedulerView, TimelineView


urlpatterns = [
    path('scheduler/', SchedulerView.as_view(), name='scheduler'),
    path('timeline/', TimelineView.as_view(), name='timeline'),
]