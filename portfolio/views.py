import re

from rest_framework import viewsets, mixins, status, views, response
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import generic, View
from django.db import IntegrityError, transaction
from django.db.models.functions import Concat
from django.db.models import Value, Count
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import *
from .forms import *
from .choices import *
from .serializers import *
from .permissions import *


class HomeRedirect(generic.RedirectView):
    url = 'home/'

class PortfollerList(generic.ListView):
    paginate_by = 15
    template_name = 'portfolio/index.html'
    model = Portfoller
    context_object_name = 'portfoller_list'

    def get_queryset(self):
        """
        Returns an filtered queryset based on the parameters passed on the GET request. 
        """
        queryset = Portfoller.objects.annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
        filter_val = self.request.GET.get('filter', '')
        filter_career = self.request.GET.get('filter_career', 'All')
        filter_country = self.request.GET.get('filter_country', 'All')
        if filter_val:
            queryset = queryset.filter(fullname__icontains=filter_val)
        if filter_career != 'All':
            queryset = queryset.filter(career=filter_career)
        if filter_country != 'All':
            queryset = queryset.filter(country_of_birth=filter_country)
        return queryset.order_by('fullname')

    def get_context_data(self, **kwargs):
        context = super(PortfollerList, self).get_context_data(**kwargs)
        context['countries'] = Portfoller.objects.distinct('country_of_birth')
        context['filter'] = self.request.GET.get('filter', '')
        context['filter_career'] = self.request.GET.get('filter_career', 'All')
        context['filter_country'] = self.request.GET.get('filter_country', 'All')
        context['career_options'] = CAREER_OPTIONS
        return context

class ProfileView(generic.DetailView):
    model = Portfoller
    template_name = 'portfolio\profile.html'    

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        self.portfoller = get_object_or_404(Portfoller, username=self.kwargs['username'])
        context['project_list'] = Project.objects.filter(user=self.portfoller).order_by('project_name')
        context['profile_owner'] = self.portfoller.profile_owner(self.request.user.username)
        return context

    def get_object(self):
        return get_object_or_404(Portfoller, username=self.kwargs['username'])

class EditProfile(LoginRequiredMixin, generic.UpdateView):
    model = Portfoller
    fields = ['first_name', 'last_name', 'gender', 'career', 'email', 'profile_picture', 'biography'] 
    template_name = 'portfolio/edit_profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    login_url = '/signin/'

    def get_success_url(self):
        """
        After the login the user is redirected to the requested profile.
        """
        return reverse('portfolio:profile', kwargs={'username': self.request.user.username})

    def get_object(self, **kwargs):
        profile_user = get_object_or_404(Portfoller, username=self.kwargs['username'])
        if profile_user.profile_owner(self.request.user.username):
            return profile_user
        raise PermissionDenied

class ProjectView(generic.DetailView):
    model = Project
    template_name = 'portfolio/project.html'
    
    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        self.portfoller = get_object_or_404(Portfoller, username=self.kwargs['username'])
        self.project = get_object_or_404(Project, user=self.portfoller, project_name=self.kwargs['project_name'])
        context['images'] = ProjectImages.objects.filter(project=self.project)
        return context

    def get_object(self):
        user = get_object_or_404(Portfoller, username=self.kwargs['username'])
        return get_object_or_404(Project, project_name=self.kwargs['project_name'], user=user)

class AddProject(LoginRequiredMixin, View):
    login_url = '/signin/'

    def get(self, request, username):
        user = get_object_or_404(Portfoller, username=username)
        if not user.profile_owner(self.request.user.username):
            raise PermissionDenied
        project = Project(user=user)
        form = AddProjectForm(initial={'user': user}, instance=project)
        formset = ProjectImagesFormSet(instance=project)
        return render(request, 'portfolio/add_project.html', {'form': form, 'formset': formset})
    
    def post(self, request, username):
        user = get_object_or_404(Portfoller, username=username)
        project = Project(user=user)
        form = AddProjectForm(request.POST, request.FILES, instance=project)
        formset = ProjectImagesFormSet(request.POST, request.FILES, instance=project)
        form.instance.user = user
        if form.is_valid():
            try:
                created_project = form.save(commit=False)
                formset = ProjectImagesFormSet(request.POST, request.FILES, instance=created_project)
                if formset.is_valid():
                    created_project.save()
                    formset.save()
                    return HttpResponseRedirect(reverse('portfolio:project', kwargs={'username': username, 'project_name': created_project.project_name}))
            except IntegrityError:
                return render(request, 'portfolio/add_project.html', {'form': form, 'formset': formset})
        else:
            return render(request, 'portfolio/add_project.html', {'form': form, 'formset': formset}) 
    
class EditProject(LoginRequiredMixin, View):
    login_url = '/signin/'

    def get(self, request, username, project_name):
        user = get_object_or_404(Portfoller, username=username)
        if not user.profile_owner(self.request.user.username):
            raise PermissionDenied
        project = Project.objects.get(user=user, project_name=project_name)
        form = EditProjectForm(instance=project)
        formset = ProjectImagesFormSet(instance=project)
        return render(request, 'portfolio/edit_project.html', {'form': form, 'formset': formset, 'project': project})
    
    def post(self, request, username, project_name):
        project = Project.objects.get(user=request.user, project_name=project_name)
        form = EditProjectForm(request.POST, request.FILES, instance=project)
        formset = ProjectImagesFormSet(request.POST, request.FILES, instance=project)
        form.instance.user = request.user
        if form.is_valid():
            try:
                created_project = form.save(commit=False)
                formset = ProjectImagesFormSet(request.POST, request.FILES, instance=created_project)
                if formset.is_valid():
                    created_project.save()
                    formset.save()
                    return HttpResponseRedirect(reverse('portfolio:project', kwargs={'username': username, 'project_name': created_project.project_name}))
            except IntegrityError:
                return render(request, 'portfolio/edit_project.html', {'form': form, 'formset': formset, 'project': project})
        else:
            return render(request, 'portfolio/edit_project.html', {'form': form, 'formset': formset, 'project': project})
    
class DeleteProject(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template = 'portfolio/delete_project.html'
    template_name = 'portfolio/delete_project.html'
    slug_field = 'project_name'
    slug_url_kwarg = 'project_name'
    login_url = '/signin/'

    def get_object(self):
        profile_user = get_object_or_404(Portfoller, username=self.kwargs['username'])
        if not profile_user.profile_owner(self.request.user.username):
            raise PermissionDenied
        return get_object_or_404(Project, user=profile_user, project_name=self.kwargs['project_name'])

    def get_success_url(self):
        return reverse('portfolio:profile', kwargs={'username': self.object.user.username})
    
    def get_context_data(self, **kwargs):
        context = super(DeleteProject, self).get_context_data(**kwargs)
        self.portfoller = get_object_or_404(Portfoller, username=self.kwargs['username'])
        context['project'] = Project.objects.get(user=self.portfoller, project_name=self.kwargs['project_name'])
        return context

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(request.GET.get('next', reverse('portfolio:home')))
        else:
            return render(request, 'portfolio\signup.html', {'form': form})
    else:
        form = SignUpForm()
    return render(request, 'portfolio\signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(request.GET.get('next', reverse('portfolio:home')))
        else:
            messages.add_message(
                request, messages.ERROR, "Incorrect user or password"
            )
        return render(request, 'portfolio\signin.html', {'form': form})
    
    else:
        form = SignInForm()
        if request.user.is_authenticated:
            return HttpResponseRedirect(request.GET.get('next', reverse('portfolio:home')))
        return render(request, 'portfolio\signin.html', {'form': form})

def signout(request):
    next_url = request.GET.get('next', reverse('portfolio:home'))
    escape_urls = ['add-project/', 'edit-project/', 'delete-project/', 'edit-profile/']
    for url in escape_urls:
        escape = re.findall(fr"{url}$", next_url)
        if escape:
            logout(request)
            return HttpResponseRedirect(reverse('portfolio:home'))
    logout(request) 
    return HttpResponseRedirect(next_url)

#API
class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return response.Response(PortfollerSerializer(user).data)

class LogoutView(views.APIView):
    def post(self, request):
        logout(request)
        return response.Response()

class PortfollerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = 'username'

    def get_queryset(self):
        queryset = Portfoller.objects.annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
        return queryset.order_by('fullname')

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePortfollerSerializer
        return PortfollerSerializer      

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes =[IsOwnerOrReadOnly]
    lookup_field = 'project_name'
    
    def get_queryset(self):
        portfoller = get_object_or_404(Portfoller, username=self.kwargs['username'])
        return Project.objects.filter(user=portfoller).order_by('project_name')

    def create(self, request, username):
        try:
            serializer = self.get_serializer(data=self.request.data)
            portfoller = Portfoller.objects.get(username=username)
            self.check_object_permissions(self.request, portfoller)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_304_NOT_MODIFIED)
            data = serializer.validated_data
            serializer.save(user=portfoller)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            raise serializers.ValidationError("Project name must be unique")
    
    def update(self, request, username, project_name, *args, **kwargs):
        try:
            portfoller = get_object_or_404(Portfoller, username=username)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            self.check_object_permissions(self.request, portfoller)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, headers=headers)
        except IntegrityError:
            raise serializers.ValidationError("Project name must be unique")

class ProjectImageViewSet(mixins.CreateModelMixin, 
                   mixins.RetrieveModelMixin, 
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = ProjectImageSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        portfoller = get_object_or_404(Portfoller, username=self.kwargs['username'])
        project = Project.objects.get(user=portfoller, project_name = self.kwargs['project_name'])
        return ProjectImages.objects.filter(project=project)

    def create(self, validated_data, username, project_name):
        serializer = self.get_serializer(data=self.request.data)
        portfoller = Portfoller.objects.get(username=username)
        project = Project.objects.get(user=portfoller, project_name=project_name)
        self.check_object_permissions(self.request, portfoller)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_304_NOT_MODIFIED)
        data = serializer.validated_data
        serializer.save(project=project)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)