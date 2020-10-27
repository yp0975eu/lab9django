from django.test import TestCase
from django.urls import reverse
from .models import Place


class TestHomePage(TestCase):
    def test_load_home_page_shows_empty_list_for_empty_database(self):
        home_page_url = reverse('place_list')
        response = self.client.get(home_page_url)
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertContains(response, 'You have no places in your wishlist')


class TestWishList(TestCase):
    fixtures = ['test_places']

    def test_view_wishlist_contains_not_visited_places(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertContains(response, 'Tokyo')
        self.assertContains(response, 'New York')
        self.assertNotContains(response, 'San Francisco')
        self.assertNotContains(response, 'Moab')


class TestVisitedPage(TestCase):
    def test_view_visited_contains_not_visited_message(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertContains(response, 'You have not visited any places')


class TestVisitedPlaces(TestCase):
    fixtures = ['test_places']

    def test_view_visitedt_contains_visited_places(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertContains(response, 'San Francisco')
        self.assertContains(response, 'Moab')
        self.assertNotContains(response, 'Tokyo')
        self.assertNotContains(response, 'New York')


class TestAddNewPlace(TestCase):
    def test_add_new_unvisited_place_to_wishlist(self):
        add_place_url = reverse('place_list')
        new_place_data = {
            'name': 'Tokyo',
            'visited': False
        }
        # make a new post request and follow redirects
        response = self.client.post(add_place_url, new_place_data, follow=True)
        # check for correct template
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # check for correct data in template
        response_places = response.context['places']
        # should be 1 item
        self.assertEqual(1, len(response_places))
        toyko_response = response_places[0]

        # check database contains correct data
        tokyo_in_database = Place.objects.get(name='Tokyo', visited=False)

        self.assertEqual(toyko_response, tokyo_in_database)


class TestVisitPlace(TestCase):
    fixtures = ['test_places']

    def test_visit_place(self):
        # get url with query string 2 - New York
        visit_place_url = reverse('place_was_visited', args=(2, ))
        # post request
        response = self.client.post(visit_place_url, follow=True)

        # check for correct template
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # check resopnse doesn't contain New York
        self.assertNotContains(response, 'New York')

        # check if new york is visited
        new_york = Place.objects.get(name='New York')
        self.assertTrue(new_york.visited)

    def test_not_visited_place(self):
        visit_place_url = reverse('place_was_visited', args=(200, ))
        response = self.client.post(visit_place_url, follow=True)
        # check for 4040 status code when posting with  non existing place
        self.assertEqual(404, response.status_code)


