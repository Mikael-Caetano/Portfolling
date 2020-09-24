import re

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import generic, View
from django.db import IntegrityError, transaction
from django.db.models.functions import Concat
from django.db.models import Value, Count
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import *
from .forms import *
from .choices import *


class HomeRedirect(generic.RedirectView):
    url = 'home/'

class PortfollerList(generic.ListView):
    paginate_by = 15
    template_name = 'portfolio/index.html'
    model = Portfoller
    context_object_name = 'portfoller_list'

    def get_queryset(self):
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
        context['project_list'] = Project.objects.filter(user=self.portfoller)
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

    def get_success_url(self):
        return reverse('portfolio:profile', kwargs={'username': self.object.username})

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
        user = Portfoller.objects.get(username=self.kwargs['username'])
        return get_object_or_404(Project, project_name=self.kwargs['project_name'], user=user)

class AddProject(LoginRequiredMixin, View):
    def get(self, request, username):
        user = get_object_or_404(Portfoller, username=request.user.username)
        project = Project(user=user)
        form = AddProjectForm(initial={'user': user}, instance=project)
        formset = ProjectImagesFormSet(instance=project)
        return render(request, 'portfolio/add_project.html', {'form': form, 'formset': formset})
    
    def post(self, request, username):
        user = get_object_or_404(Portfoller, username=request.user.username)
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
                    return HttpResponseRedirect(reverse('portfolio:project', kwargs={'username': request.user.username, 'project_name': created_project.project_name}))
            except IntegrityError:
                return render(request, 'portfolio/add_project.html', {'form': form, 'formset': formset})
        else:
            return render(request, 'portfolio/add_project.html', {'form': form, 'formset': formset}) 
    
    def get_context_data(self, **kwargs):
        context = super(AddProject, self).get_context_data(**kwargs)
        self.portfoller = get_object_or_404(Portfoller, username=self.kwargs['username'])
        return context
    
class EditProject(LoginRequiredMixin, View):
    def get(self, request, username, project_name):
        project = Project.objects.get(user=self.request.user, project_name=project_name)
        form = EditProjectForm(instance=project)
        formset = ProjectImagesFormSet(instance=project)
        return render(request, 'portfolio/edit_project.html', {'form': form, 'formset': formset})
    
    def post(self, request, username, project_name):
        project = Project.objects.get(user=self.request.user, project_name=project_name)
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
                    return HttpResponseRedirect(reverse('portfolio:project', kwargs={'username': request.user.username, 'project_name': created_project.project_name}))
            except IntegrityError:
                return render(request, 'portfolio/edit_project.html', {'form': form, 'formset': formset})
        else:
            return render(request, 'portfolio/edit_project.html', {'form': form, 'formset': formset})

    def get_context_data(self, **kwargs):
        context = super(EditProject, self).get_context_data(**kwargs)
        self.portfoller = get_object_or_404(Portfoller, username=self.kwargs['username'])
        context['project'] = Project.objects.get(user=self.portfoller, project_name=self.kwargs['project_name'])
        return context
    
class DeleteProject(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template = 'portfolio/delete_project.html'
    template_name = 'portfolio/delete_project.html'
    slug_field = 'project_name'
    slug_url_kwarg = 'project_name'

    def get_object(self):
        project = Project.objects.get(user=self.request.user, project_name=self.kwargs['project_name'])
        return project

    def get_success_url(self):
        return reverse('portfolio:profile', kwargs={'username': self.object.user.username})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(request.GET.get('next', ''))
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
            return HttpResponseRedirect(request.GET.get('next', ''))
        else:
            messages.add_message(
                request, messages.ERROR, "Incorrect user or password"
            )
        return render(request, 'portfolio\signin.html', {'form': form})
    
    else:
        form = SignInForm()
        if request.user.is_authenticated:
            return HttpResponseRedirect(request.GET.get('next', ''))
        return render(request, 'portfolio\signin.html', {'form': form})

def signout(request):
    next_url = request.GET.get('next', '')
    escape_urls = ['add-project/', 'edit-project/', 'delete-project/', 'edit-profile/']
    for url in escape_urls:
        escape = re.findall(fr"{url}$", next_url)
        if escape:
            logout(request)
            return HttpResponseRedirect(reverse('portfolio:home'))
    logout(request) 
    return HttpResponseRedirect(next_url)