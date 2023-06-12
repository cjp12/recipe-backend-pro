"""url mappings for the user api"""

from django.urls import path

from user import views

# This app name is the reverse url used in the test. path below in url pat.
app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name = 'create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name = 'me')
]
