from django.urls import path
from .views import TnCView


urlpatterns=[
    path('terms_n_conditions', TnCView.as_view(), name='terms&conditions')
]