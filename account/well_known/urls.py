from account.well_known import views
from django.urls import path

#######################
# Note: This url config must be included at /.well-known/, if it is included.
#######################

urlpatterns = [

    path('change-password',
         views.change_password),

]
