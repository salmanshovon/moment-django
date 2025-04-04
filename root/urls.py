from django.urls import path
from .views import TnCView, RootView, OfflineView, PrivacyPolicyView, FeaturesView, PriceView, ContactUsView, ContactMailSendView, AboutUsView


urlpatterns=[
    path('terms_n_conditions', TnCView.as_view(), name='terms&conditions'),
    path('', RootView.as_view(), name='root'),
    path('offline/', OfflineView.as_view(), name='offline'),
    path('privacy_policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('features/', FeaturesView.as_view(), name='features'),
    path('pricing/', PriceView.as_view(), name='pricing'),
    path('contact_us/', ContactUsView.as_view(), name='contact_us'),
    path('post_email_msg/', ContactMailSendView.as_view(), name='contact_email_submit'),
    path('about_us/', AboutUsView.as_view(), name='about_us'),
]