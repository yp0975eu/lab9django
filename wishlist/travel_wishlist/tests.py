from django.test import TestCase
from django.urls import reverse
from django.test import override_settings

from django.contrib.auth.models import User
from .models import Place

import tempfile
import filecmp
import os
from PIL import Image

class TestHomePage(TestCase):

    fixtures = ['test_users']

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)

    def test_load_home_page_shows_empty_list_for_empty_database(self):
        home_page_url = reverse('place_list')
        response = self.client.get(home_page_url)
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertContains(response, 'You have no places in your wishlist')


class TestWishList(TestCase):
    # Load this data into the database for all of the tests in this class
    fixtures = ['test_places', 'test_users']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

    def test_view_wishlist_contains_not_visited_places(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertContains(response, 'New York')
        self.assertContains(response, 'San Francisco')
        self.assertNotContains(response, 'Tokyo')
        self.assertNotContains(response, 'Moab')


class TestVisitedPage(TestCase):
    # Load this data into the database for all of the tests in this class
    fixtures = ['test_users']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

    def test_view_visited_contains_not_visited_message(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertContains(response, 'You have not visited any places')


class TestVisitedPlaces(TestCase):
    fixtures = ['test_places', 'test_users']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

    def test_view_visited_contains_visited_places(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertContains(response, 'Tokyo')
        self.assertContains(response, 'Moab')
        self.assertNotContains(response, 'San Francisco')
        self.assertNotContains(response, 'New York')


class TestAddNewPlace(TestCase):
    fixtures = ['test_users']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

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
    fixtures = ['test_places', 'test_users']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

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
        # check for 404 status code when posting with  non existing place
        self.assertEqual(404, response.status_code)


class TestPlace(TestCase):
    # Load this data into the database for all of the tests in this class
    fixtures = ['test_places', 'test_users']

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)


    def test_modify_someone_else_place_not_authorized(self):
        response = self.client.post(reverse('place', kwargs={'place_pk':5}), {'notes':'awesome'}, follow=True)
        self.assertEqual(403, response.status_code)   # 403 Forbidden 
        

    def test_place(self):
        place_1 = Place.objects.get(pk=1)

        response = self.client.get(reverse('place', kwargs={'place_pk':1} ))
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/place.html')

        # What data was sent to the template?
        data_rendered = response.context['place']

        # Same as data sent to template?
        self.assertEqual(data_rendered, place_1)

        # and correct data shown on page?
    
        self.assertContains(response, 'Tokyo') 
        self.assertContains(response, 'cool')  
        self.assertContains(response, 'Jan. 1, 2014') 
            
        # TODO how to test correct image is shown?


    def test_modify_notes(self):

        response = self.client.post(reverse('place', kwargs={'place_pk':1}), {'notes':'awesome'}, follow=True)

        updated_place_1 = Place.objects.get(pk=1)

        # db updated?
        self.assertEqual('awesome', updated_place_1.notes)

        self.assertEqual(response.context['place'], updated_place_1)
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/place.html')

        # and correct data shown on page?
        self.assertNotContains(response, 'cool')  # old text is gone 
        self.assertContains(response, 'awesome')  # new text shown
       

    def test_add_notes(self):

        response = self.client.post(reverse('place', kwargs={'place_pk':4}), {'notes':'yay'}, follow=True)

        updated_place_4 = Place.objects.get(pk=4)

        # db updated?
        self.assertEqual('yay', updated_place_4.notes)

        # Correct object used in response?
        self.assertEqual(response.context['place'], updated_place_4)
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/place.html')

        # and correct data shown on page?
        self.assertContains(response, 'yay')  # new text shown
       

    def test_add_date_visited(self):

        date_visited = '2014-01-01'

        response = self.client.post(reverse('place', kwargs={'place_pk':4}), {'date_visited': date_visited}, follow=True)

        updated_place_4 = Place.objects.get(pk=4)

        # Database updated correctly?
        self.assertEqual(updated_place_4.date_visited.isoformat(), date_visited)   # .isoformat is YYYY-MM-DD

        # Right object sent to template?
        self.assertEqual(response.context['place'], updated_place_4)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/place.html')

        # and correct data shown on page?
        self.assertContains(response, 'Jan. 1, 2014')  # new text shown
       


# class TestImageUpload(TestCase):

#     fixtures = ['test_users', 'places']

#     def setUp(self):
#         user = User.objects.get(pk=1)
#         self.client.force_login(user)
#         self.MEDIA_ROOT = tempfile.mkdtemp()
        

#     def tearDown(self):
#         print('todo delete temp directory, temp image')


#     def create_temp_image_file(self):
#         handle, tmp_img_file = tempfile.mkstemp(suffix='.jpg')
#         img = Image.new('RGB', (10, 10) )
#         img.save(tmp_img_file, format='JPEG')
#         return tmp_img_file


#     def test_upload_new_image_for_own_place(self):
        
#         img_file_path = self.create_temp_image_file()

#         with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
#             with open(img_file_path, 'rb') as img_file:
#                 resp = self.client.post(reverse('place', kwargs={'place_pk': 1} ), {'photo': img_file }, follow=True)
                
#                 self.assertEqual(200, resp.status_code)

#                 place_1 = Place.objects.get(pk=1)
#                 img_file_name = os.path.basename(img_file_path)
#                 expected_uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'user_images', img_file_name)

#                 self.assertTrue(os.path.exists(expected_uploaded_file_path))
#                 self.assertIsNotNone(place_1.photo)
#                 self.assertTrue(filecmp.cmp( img_file_path,  expected_uploaded_file_path ))


#     def test_change_image_for_own_place_expect_old_deleted(self):
        
#         first_img_file_path = self.create_temp_image_file()
#         second_img_file_path = self.create_temp_image_file()

#         with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
#             with open(first_img_file_path, 'rb') as first_img_file:

#                 resp = self.client.post(reverse('place', kwargs={'place_pk': 1} ), {'photo': first_img_file }, follow=True)

#                 place_1 = Place.objects.get(pk=1)

#                 first_uploaded_image = place_1.photo.name

#                 with open(second_img_file_path, 'rb') as second_img_file:
#                     resp = self.client.post(reverse('place', kwargs={'place_pk':1}), {'photo': second_img_file}, follow=True)

#                     # first file should not exist 
#                     # second file should exist 

#                     place_1 = Place.objects.get(pk=1)

#                     second_uploaded_image = place_1.photo.name

#                     first_path = os.path.join(self.MEDIA_ROOT, first_uploaded_image)
#                     second_path = os.path.join(self.MEDIA_ROOT, second_uploaded_image)

#                     self.assertFalse(os.path.exists(first_path))
#                     self.assertTrue(os.path.exists(second_path))


#     def test_upload_image_for_someone_else_place(self):

#         with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
  
#             img_file = self.create_temp_image_file()
#             with open(img_file, 'rb') as image:
#                 resp = self.client.post(reverse('place', kwargs={'place_pk': 5} ), {'photo': image }, follow=True)
#                 self.assertEqual(403, resp.status_code)

#                 place_5 = Place.objects.get(pk=5)
#                 self.assertFalse(place_5.photo)   # no photo set


#     def test_delete_place_with_image_image_deleted(self):
        
#         img_file_path = self.create_temp_image_file()

#         with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
#             with open(img_file_path, 'rb') as img_file:
#                 resp = self.client.post(reverse('place', kwargs={'place_pk': 1} ), {'photo': img_file }, follow=True)
                
#                 self.assertEqual(200, resp.status_code)

#                 place_1 = Place.objects.get(pk=1)
#                 img_file_name = os.path.basename(img_file_path)
                
#                 uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'user_images', img_file_name)

#                 # delete place 1 

#                 place_1 = Place.objects.get(pk=1)
#                 place_1.delete()

#                 self.assertFalse(os.path.exists(uploaded_file_path))
               