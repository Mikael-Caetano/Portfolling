from rest_framework import serializers

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from .models import *
from .choices import *

from django_countries.serializers import CountryFieldMixin


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])

        if not user:
            raise serializers.ValidationError('Incorrect email or password.')

        return {'user': user}

class CreatePortfollerSerializer(CountryFieldMixin, serializers.ModelSerializer):
    def create(self, validated_data):
        """
        Create and return a new `Portfoller` instance, given the validated data, with a hashed password.
        """
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    class Meta:
        model = Portfoller
        fields = ('username', 'password', 'first_name', 'last_name', 'gender', 'birthdate', 
        'country_of_birth', 'career', 'email', 'profile_picture', 'biography')

class PortfollerSerializer(CountryFieldMixin, serializers.ModelSerializer):
    projects = serializers.SlugRelatedField(many=True, read_only=True, slug_field='project_name')
    
    def update(self, instance, validated_data):
        """
        Update and return an existing `Portfoller` instance, given the validated data.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.career = validated_data.get('career', instance.career)
        instance.email = validated_data.get('email', instance.email)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.biography = validated_data.get('biography', instance.biography)
        instance.save()
        return instance

    class Meta:
        model = Portfoller
        fields = ('username', 'first_name', 'last_name', 'gender', 'birthdate', 'country_of_birth', 'career',
        'email', 'profile_picture', 'biography', 'projects')
    
class ProjectSerializer(serializers.ModelSerializer):
    portfoller = PortfollerSerializer(many=False, read_only=True)

    class Meta:
        model = Project
        fields = ['portfoller', 'project_name', 'project_description']

class ProjectImageSerializer(serializers.ModelSerializer):
    project_instance = ProjectSerializer(many=False, read_only=True)

    class Meta:
        model = ProjectImages
        fields = ['pk', 'project_instance', 'image']
        