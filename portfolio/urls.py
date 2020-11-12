from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static 
from rest_framework.routers import DefaultRouter
from . import views, models

app_name = 'portfolio'

#API URLs
router = DefaultRouter()
router.register('portfollers', views.PortfollerViewSet, basename='portfollers')
router.register('portfollers/(?P<username>\w+)/projects', views.ProjectViewSet, basename='projects')
router.register('portfollers/(?P<username>\w+)/projects/(?P<project_name>\w+)/images', views.ProjectImageViewSet, basename='images')

#URLs when in a project page.
urlprojects = [
    path('', views.ProjectView.as_view(), name='project'),
    path('edit-project/', views.EditProject.as_view(), name='edit_project'),
    path('delete-project/', views.DeleteProject.as_view(), name='delete_project'),
]

#URLs when in a Portfoller page.
urlusers = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('edit-profile/', views.EditProfile.as_view(), name='edit_profile'),
    path('add-project/', views.AddProject.as_view(), name='add_project'),
    path('<str:project_name>/', include(urlprojects)),
]

#URLs when in the website.
urlpatterns = [
    path('', views.HomeRedirect.as_view(), name='home-redirect'),
    path('home/', views.PortfollerList.as_view(), name='home'),
    path('users/<str:username>/', include(urlusers)),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('api/', include(router.urls)),
    path('api/login/', views.LoginView.as_view(), name='api-login'),
    path('api/logout/', views.LogoutView.as_view(), name='api-logout'),
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 