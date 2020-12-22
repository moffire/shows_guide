from django.urls import path
from .views import MainView, MovieDetail

app_name = 'shows'

urlpatterns = [
    path('', MainView.as_view(), name='main_page'),
    path('<str:rating>/', MainView.as_view(), name='main_page'),
    path('<int:external_id>/', MovieDetail.as_view(), name='detail'),
]
