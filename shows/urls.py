from django.urls import path
from .views import MainPageView, MovieDetail, SearchView, RatingView

app_name = 'shows'

urlpatterns = [
    path('', MainPageView.as_view(), name='index'),
    path('<str:rating>/', RatingView.as_view(), name='rating'),
    path('details/<int:external_id>/', MovieDetail.as_view(), name='detail'),
    path('search', SearchView.as_view(), name='search'),
]
