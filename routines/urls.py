from django.urls import path
from .views import SchedulerView


urlpatterns = [
    path('scheduler/', SchedulerView.as_view(), name='scheduler'),
]