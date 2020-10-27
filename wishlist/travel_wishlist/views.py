from django.shortcuts import render, redirect
from .models import Place
from .forms import NewPlaceForm

# Create your views here.

def place_list(request):
    if request.method == 'POST':
        form = NewPlaceForm(request.POST)
        place = form.save() # creates a new place
        if form.is_valid():
            place.save() # saves to db
            return redirect('place_list')

    places = Place.objects.filter(visited=False).order_by('name')
    new_place_form = NewPlaceForm()
    data = {
        'places': places,
        'new_place_form': new_place_form 
    }
    return render(request, 'travel_wishlist/wishlist.html', data)

def places_visited(request):
    visited = Place.objects.filter(visited=True)
    data = {
        'visited': visited
    }
    return render(request, 'travel_wishlist/visited.html', data)