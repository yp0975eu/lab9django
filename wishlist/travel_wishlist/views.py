from django.shortcuts import render, redirect, get_object_or_404
from .models import Place
from .forms import NewPlaceForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def place_list(request):
    if request.method == 'POST':
        form = NewPlaceForm(request.POST) # create new form from post data
        place = form.save(commit=False) #creates a new place, dont commit when creating
        place.user = request.user # add logged in user to place model
        if form.is_valid(): # check against db constraints
            place.save() # saves to db
            return redirect('place_list')

    # if not post - query Place model with filters and order applied
    places = Place.objects.filter(user=request.user).filter(visited=False).order_by('name')
    new_place_form = NewPlaceForm()
    data = {
        'places': places,
        'new_place_form': new_place_form 
    }
    return render(request, 'travel_wishlist/wishlist.html', data)

@login_required
def places_visited(request):
    visited = Place.objects.filter(user=request.user).filter(visited=True)
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
