import os
import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from django_countries.fields import CountryField

from .choices import *
from .validators import *


#Setting directory path to profiles pictures
def profile_picture_path(instance, filename):
    """
    Returns the directory path where the profile image will be saved.
    """
    return os.path.join("images", "user_%s" % instance.username, "profile_image", filename)

#Setting directory path to project images
def project_images_path(instance, filename):
    """
    Returns the directory path where the project images will be saved.
    """
    return os.path.join("images", "user_%s" % instance.project.user.username, "project_%s" % instance.project.project_name, filename)

class Portfoller(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=6, choices=GENDER_OPTIONS, default='Male')
    birthdate = models.DateField('birthdate', validators=[validate_birthdate])
    country_of_birth = CountryField()
    career = models.CharField(max_length=20, choices=CAREER_OPTIONS, default='Developer')
    email = models.EmailField(max_length=254, unique=True)
    profile_picture = models.ImageField(upload_to=profile_picture_path, default='generic_user.png', validators=[validate_file_size])
    biography = models.TextField(max_length=1000, null=True, blank=True)

    REQUIRED_FIELDS = ['password', 'first_name', 'last_name', 'birthdate', 'country_of_birth', 'email']

    def get_age(self):
        now = timezone.now()
        return now.year - self.birthdate.year - ((now.month, now.day) < (self.birthdate.month, self.birthdate.day))
    
    def profile_owner(self, request_username):
        """
        Verify if the request user is the owner of the Portfoller instance, its used to validate owner only actions.
        """
        return request_username == self.username

    def __str__(self):
        s = ' '
        return s.join([self.first_name, self.last_name])

class Project(models.Model):
    user = models.ForeignKey(Portfoller, related_name='projects', on_delete=models.CASCADE)
    project_name = models.CharField(max_length=50, validators=[validate_project_name])
    project_description = models.TextField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.project_name

    class Meta:
        #The project name must be unique in the Portfoller profile.
        unique_together = ('project_name', 'user')

class ProjectImages(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=project_images_path, null=True, blank=True, validators=[validate_file_size])