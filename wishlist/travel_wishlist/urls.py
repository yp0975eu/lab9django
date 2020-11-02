
from django.urls import path
from . import views

urlpatterns = [
    path('', views.place_list, name='place_list'),
    path('visited', views.places_visited, name='places_visited'),
    path('place/<int:place_pk>/was_visited', views.place_was_visited, name='place_was_visited'),
    path('place/<int:place_pk>/delete', views.delete_place, name='delete_place'),
    path('place/<int:place_pk>', views.place, name='place')
]