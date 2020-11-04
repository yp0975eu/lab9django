from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.core.files.storage import default_storage

class Place(models.Model):
    user = models.ForeignKey('auth.User', null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    visited = models.BooleanField(default=False)
    date_visited = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='user_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        old_place = Place.objects.filter(pk=self.pk).first() # get the old place
        # if there is an old place and it has a photo
        if old_place and old_place.photo:
            # check if it is not the same photo as the new photo
            if old_place.photo != self.photo:
                self.delete_photo(old_place.photo)
        super().save(*args, **kwargs)

    def delete_photo(self, photo):
        # check for photo by name
        if default_storage.exists(photo.name):
            #delete if it exists
            default_storage.delete(photo.name)

    def delete(self, *args, **kwargs):
        # when place model is deleted, delete the photo if it exists
        if self.photo:
            self.delete_photo(self.photo)
        super().delete(*args, **kwargs)

        
    def __str__(self):
        photo_str = self.photo.url if self.photo else 'no photo'
        return f'{self.pk}: {self.name}, visited? {self.visited} on {self.date_visited}\nPhoto {photo_str}'

class DateInput(forms.DateInput):
    input_type = 'date'

class TripReviewForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('notes', 'date_visited', 'photo')
        widgets = {
            'date_visited': DateInput()
        }