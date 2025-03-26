from django.urls import path
from .views import TnCView, RootView, OfflineView


urlpatterns=[
    path('terms_n_conditions', TnCView.as_view(), name='terms&conditions'),
    path('', RootView.as_view(), name='root'),
    path('offline/', OfflineView.as_view(), name='offline'),
]