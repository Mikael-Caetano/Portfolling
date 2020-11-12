from dateutil.relativedelta import relativedelta

from django.conf import settings
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone, dateformat

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .widgets import NamedFileInput, DatePicker
from .models import *
from .choices import *


class SignUpForm(UserCreationForm):
    class Meta:
        model = Portfoller
        fields = ('profile_picture', 'username', 'first_name', 'last_name', 'gender', 'birthdate', 'country_of_birth', 'career', 'biography', 'email', 'password1', 'password2', )
        widgets = {
        #Birthdate can be in a range from 120 years ago to the present day.
        'birthdate': DatePicker(attrs={
        'min': dateformat.format(timezone.now() - relativedelta(years=120), 'Y-m-d'),
        'max': dateformat.format(timezone.now(), 'Y-m-d')}),
        'country_of_birth':CountrySelectWidget,
        'biography': forms.Textarea}
    
class SignInForm(AuthenticationForm):
    pass

class AddProjectForm(forms.ModelForm):
    def clean(self):
        #Verify if project_name is unique in the owner profile.
        cleaned_data = super().clean()
        project_name = cleaned_data.get("project_name")
        user = self.instance.user
        user_project_list = Project.objects.filter(user=user)
        if user and project_name:
            for project in user_project_list:
                if project.project_name == project_name:
                    raise forms.ValidationError("Your profile already has a project with this name. ")
                    break
    class Meta:
        model = Project
        fields = ['project_name', 'project_description']

class EditProjectForm(forms.ModelForm):
    def clean(self):
        #Verify if project_name is unique in the owner profile.
        cleaned_data = super().clean()
        project_name = cleaned_data.get("project_name")
        user = self.instance.user
        user_project_list = Project.objects.filter(user=user)
        project_name_count = 0
        if user and project_name:
            for project in user_project_list:
                if project.project_name == project_name:
                    project_name_count = project_name_count + 1
            if project_name_count >= 2:
                raise forms.ValidationError("Your profile already has a project with this name. ")

    class Meta:
        model = Project
        fields = ['project_name','project_description']

#Inlineformset to manage project images in the AddProjectForm and EditProjectForm
ProjectImagesFormSet = forms.inlineformset_factory(Project, ProjectImages, fields=('image',), extra=1, widgets={'image': NamedFileInput}, max_num=30)