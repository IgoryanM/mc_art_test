from django.urls import path

from .views import get_val_view, get_dif_view

urlpatterns = [
    path('get-val/', get_val_view),
    path('get-dif/<val>/<date_one>/<date_two>/', get_dif_view),
]
