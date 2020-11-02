from django.shortcuts import render, redirect, get_object_or_404
from .models import Place
from .forms import NewPlaceForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
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

@login_required
def places_visited(request):
    visited = Place.objects.filter(visited=True)
    data = {
        'visited': visited
    }
    return render(request, 'travel_wishlist/visited.html', data)

@login_required
def place_was_visited(request, place_pk):
    """
    If this is a post request, find the place by key and set visited to true,
    then redirect. Return 404 if not found.
    Redirect to place_list if not a post request.
    """
    if request.method == 'POST':
        place = get_object_or_404(Place, pk=place_pk)
        place.visited = True
        place.save()

    return redirect('place_list')
