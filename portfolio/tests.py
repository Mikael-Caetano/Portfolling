import os
from dateutil.relativedelta import relativedelta
import mock

from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.files import File
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from .models import *


#Testing Functions
def create_portfoller(username, first_name=None, last_name=None, email=None, password='testpassword', gender='Male', birthdate='2000-01-01', country_of_birth='BR', career='Developer', biography=None):
    """
    Create a portfoller with the given `username` and `password`, and gives it
    all the other fields information.
    Returns the created portfoller.
    """
    first_name = username
    last_name = username
    email = username + '@testmail.com'
    return Portfoller.objects.create_user(username=username, password=password, first_name=first_name,
    last_name=last_name, gender=gender, birthdate=birthdate, country_of_birth=country_of_birth,
    career=career, email=email, biography=biography)

def create_multi_portfoller(n):
    """
    Create `n` portfollers with a autogenerate username and
    password, and gives it all the other fields information.
    Returns a list with all created portfollers.
    """
    portfollers = []
    for x in range(1, n + 1):
        username = 'test' + str(x)
        portfoller = create_portfoller(username=username)
        portfollers.append(portfoller)
    return portfollers

def create_project(portfoller, project_name, project_description):
    """
    Create a project with the given `project_name` and 
    `project_description` to the given `portfoller`.
    """
    return Project.objects.create(user=portfoller, project_name=project_name, project_description=project_description)

def get_expected(portfollers):
    expected_queryset = []
    for portfoller in portfollers:
        expected = '<Portfoller: ' + portfoller.first_name + ' ' + portfoller.last_name + '>'
        expected_queryset.append(expected)
    return expected_queryset

#Models
class PortfollerModelTests(TestCase):
    def test_get_age(self):
        """
        Portfoller age is calculated correctly from `birthdate`.
        """
        portfoller_1_age = 60
        portfoller_2_age = 42
        portfoller_3_age = 12
        portfoller_1 = create_portfoller('test1', birthdate=timezone.now() - relativedelta(years=portfoller_1_age))
        portfoller_2 = create_portfoller('test2', birthdate=timezone.now() - relativedelta(years=portfoller_2_age))
        portfoller_3 = create_portfoller('test3', birthdate=timezone.now() - relativedelta(years=portfoller_3_age))
        self.assertEqual(portfoller_1.get_age(), portfoller_1_age)
        self.assertEqual(portfoller_2.get_age(), portfoller_2_age)
        self.assertEqual(portfoller_3.get_age(), portfoller_3_age)


#Views
class PortfollerListViewTests(TestCase):
    def test_no_portfollers(self):
        """
        If no portfollers exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Portfollers are available.")
        self.assertQuerysetEqual(response.context['portfoller_list'], [])
        self.assertTemplateUsed('portfolio/index.html')

    def test_one_portfoller(self):
        """
        Existent user is shown in the home page.
        """
        portfoller_1 = create_portfoller('test1')
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['portfoller_list'], ['<Portfoller: test1 test1>'])
        self.assertNotContains(response, "No Portfollers are available.")
        self.assertTemplateUsed('portfolio/index.html')

    def test_four_portfollers(self):
        """
        Existent users are shown in the home page.
        """
        expected = get_expected(create_multi_portfoller(4))
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['portfoller_list'], expected)
        self.assertNotContains(response, "No Portfollers are available.")
        self.assertTemplateUsed('portfolio/index.html')

    def test_countries_context_data(self):
        """
        Countries context data gives uniques countries objects.
        """
        portfoller1 = create_portfoller('test1', country_of_birth='US')
        portfoller2 = create_portfoller('test2')
        portfoller3 = create_portfoller('test3')
        countries = [portfoller1.country_of_birth, portfoller2.country_of_birth]
        response = self.client.get(reverse('portfolio:home'))
        portfollers = response.context['countries']
        context_countries = []
        for portfoller in portfollers:
            context_countries.append(portfoller.country_of_birth)
        self.assertCountEqual(countries, context_countries)

    def text_filter_context_data(self):
        """
        Filters context data gives the correct value captured from URL.
        """
        response = self.client.get('/home/?filter=a&filter_career=Developer&filter_country=BR')
        filter_context_get = self.client.request.GET.get('filter', '')
        filter_career_get = self.client.request.GET.get('filter_career', '')
        filter_country_get = self.client.request.GET.get('filter_country', '')
        filter_context = response.context['filter']
        filter_career = response.context['filter_career']
        filter_country = response.context['filter_country']
        self.assertEqual(filter_context_get, filter_context)
        self.assertEqual(filter_career_get, filter_career)
        self.assertEqual(filter_country_get, filter_country)

class ProfileViewTests(TestCase):
    def test_context_data(self):
        """
        `project_list` context data contains the correct values.
        """
        portfoller = create_portfoller('Test')
        project = create_project(portfoller, 'Test_project', 'Test')
        response = self.client.get(reverse('portfolio:profile', kwargs={'username': portfoller.username}))
        project_list = response.context['project_list']
        portfoller_project_list = Project.objects.filter(user=portfoller).order_by('project_name')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(project_list, portfoller_project_list, transform=lambda x: x)

class EditProfileViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portfoller = create_portfoller('Test')
        cls.portfoller2 = create_portfoller('Test2')
        cls.sign_in_url = reverse('portfolio:signin') + '?next=' + reverse('portfolio:edit_profile', kwargs={'username': cls.portfoller.username})

    def test_not_logged_user_not_owner(self):
        """
        Not logged user are redirected to sign in page and if it don't sign in the edit_profile
        requested profile, a `PermissionDenied` error is raised.
        """
        response = self.client.get(reverse('portfolio:edit_profile', kwargs={'username': self.portfoller.username}), follow=True)
        self.assertRedirects(response, self.sign_in_url)
        response = self.client.post(self.sign_in_url, {'username': 'Test2', 'password': 'testpassword'}, follow=True)
        self.assertEqual(response.status_code, 403)
    
    def test_not_logged_user_owner(self):
        """
        Not logged user are redirected to sign in page and if it sign in the edit_profile
        requested profile, it's redirected to the edit_profile page.
        """
        response = self.client.get(reverse('portfolio:edit_profile', kwargs={'username': self.portfoller.username}), follow=True)
        self.assertRedirects(response, self.sign_in_url)
        response = self.client.post(self.sign_in_url, {'username': 'Test', 'password': 'testpassword'}, follow=True)
        self.assertRedirects(response, reverse('portfolio:edit_profile', kwargs={'username': self.portfoller.username}))

    def test_logged_user_not_owner(self):
        """
        Logged user who is not the owner of the edit_profile requested profile raises a
        `PermissionDenied` error.
        """ 
        response = self.client.post('/signin/', {'username': 'Test2', 'password': 'testpassword'})
        response = self.client.get(reverse('portfolio:edit_profile', kwargs={'username': self.portfoller.username}))
        self.assertEqual(response.status_code, 403)

    def test_logged_user_owner(self):
        """
        Logged user who is the owner of the edit_profile requested profile is redirected
        to the edit_profile page.
        """
        response = self.client.post('/signin/', {'username': 'Test', 'password': 'testpassword'})
        response = self.client.get(reverse('portfolio:edit_profile', kwargs={'username': self.portfoller.username}))
        self.assertEqual(response.status_code, 200)
    
    def test_profile_updated(self):
        """
        The Portfoller instance has its data updated.
        """
        self.assertEqual(self.portfoller.first_name, 'Test')
        response = self.client.post('/signin/', {'username': 'Test', 'password': 'testpassword'})
        with open(os.getcwd() + '/portfoling/media/test_media/test_image.png', 'rb') as profile_picture:
            response = self.client.post(reverse('portfolio:edit_profile', kwargs={'username': self.portfoller.username}), data={'profile_picture': profile_picture, 'username': self.portfoller.username, 'first_name': 'Updated', 'last_name': 'Updated', 'gender': 'Male', 'career': 'Developer', 'email': 'updatedmail@updatedmail.com'})
        self.portfoller.refresh_from_db()
        self.assertEqual(self.portfoller.first_name, 'Updated')

class ProjectViewTests(TestCase):
    def test_context_data(self):
        """
        `images` context data contains the correct values.
        """
        portfoller = create_portfoller('Test')
        project = create_project(portfoller, 'test_project', 'test_project_description')
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        project_image = ProjectImages(project, file_mock)
        project_image.image = open(os.getcwd() + '/portfoling/media/test_media/test_image.png')
        response = self.client.get(reverse('portfolio:project', kwargs={'username': portfoller.username, 'project_name': project.project_name}))
        response_images = response.context['images']
        project_images = ProjectImages.objects.filter(project=project)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(project_images, response_images, transform=lambda x: x)

class AddProjectViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portfoller = create_portfoller('Test')
        cls.portfoller2 = create_portfoller('Test2')
        cls.sign_in_url = reverse('portfolio:signin') + '?next=' + reverse('portfolio:add_project', kwargs={'username': cls.portfoller.username})

    def test_not_logged_user_not_owner(self):
        """
        Not logged user are redirected to sign in page and if it don't sign in the add_project
        requested profile, a `PermissionDenied` error is raised.
        """
        response = self.client.get(reverse('portfolio:add_project', kwargs={'username': self.portfoller.username}), follow=True)
        self.assertRedirects(response, self.sign_in_url)
        response = self.client.post(self.sign_in_url, {'username': 'Test2', 'password': 'testpassword'}, follow=True)
        self.assertEqual(response.status_code, 403)
    
    def test_not_logged_user_owner(self):
        """
        Not logged user are redirected to sign in page and if it sign in the add_project
        requested profile, it's redirected to the add_project page.
        """
        response = self.client.get(reverse('portfolio:add_project', kwargs={'username': self.portfoller.username}), follow=True)
        self.assertRedirects(response, self.sign_in_url)
        response = self.client.post(self.sign_in_url, {'username': 'Test', 'password': 'testpassword'}, follow=True)
        self.assertRedirects(response, reverse('portfolio:add_project', kwargs={'username': self.portfoller.username}))

    def test_logged_user_not_owner(self):
        """
        Logged user who is not the owner of the add_project requested profile raises a
        `PermissionDenied` error.
        """ 
        response = self.client.post('/signin/', {'username': 'Test2', 'password': 'testpassword'})
        response = self.client.get(reverse('portfolio:add_project', kwargs={'username': self.portfoller.username}))
        self.assertEqual(response.status_code, 403)

    def test_logged_user_owner(self):
        """
        Logged user who is the owner of the add_project requested profile is redirected
        to the add_project page.
        """
        response = self.client.post('/signin/', {'username': 'Test', 'password': 'testpassword'})
        response = self.client.get(reverse('portfolio:add_project', kwargs={'username': self.portfoller.username}))
        self.assertEqual(response.status_code, 200)

    def test_project_added(self):
        """
        The project is successfully created.
        """
        self.assertEqual(Project.objects.filter(user=self.portfoller).count(), 0)
        response = self.client.post('/signin/', {'username': 'Test', 'password': 'testpassword'})
        response = self.client.get(reverse('portfolio:add_project', kwargs={'username': self.portfoller.username}))
        response = self.client.post(reverse('portfolio:add_project', kwargs={'username': self.portfoller.username}), data={
            'project_name': 'test_project', 'project_description': 'This is a test project.', 'projectimages_set-TOTAL_FORMS': 1,
            'projectimages_set-INITIAL_FORMS': 0, 'projectimages_set-MIN_NUM_FORMS': 0, 'projectimages_set-MAX_NUM_FORMS': 30})
        self.assertEqual(Project.objects.filter(user=self.portfoller).count(), 1)

class EditProjectViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portfoller = create_portfoller('Test')
        cls.portfoller_project = create_project(cls.portfoller, 'Test_project', 'Test_description')
        cls.portfoller2 = create_portfoller('Test2')
        cls.sign_in_url = reverse('portfolio:signin') + '?next=' + reverse('portfolio:edit_project', kwargs={'username': cls.portfoller.username, 'project_name': cls.portfoller_project.project_name})

    def test_not_logged_user_not_owner(self):
        """
        Not logged user are redirected to sign in page and if it don't sign in the edit_project
        requested profile, a `PermissionDenied` error is raised.
        """
        response = self.client.get(reverse('portfolio:edit_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}), follow=True)
        self.assertRedirects(response, self.sign_in_url)
        response = self.client.post(self.sign_in_url, {'username': 'Test2', 'password': 'testpassword'}, follow=True)
        self.assertEqual(response.status_code, 403)
    
    def test_not_logged_user_owner(self):
        """
        Not logged user are redirected to sign in page and if it sign in the edit_project
        requested profile, it's redirected to the edit_project page.
        """
        response = self.client.get(reverse('portfolio:edit_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}), follow=True)
        self.assertRedirects(response, self.sign_in_url)
        response = self.client.post(self.sign_in_url, {'username': 'Test', 'password': 'testpassword'}, follow=True)
        self.assertRedirects(response, reverse('portfolio:edit_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}))

    def test_logged_user_not_owner(self):
        """
        Logged user who is not the owner of the edit_project requested profile raises a
        `PermissionDenied` error.
        """ 
        response = self.client.post('/signin/', {'username': 'Test2', 'password': 'testpassword'})
        response = self.client.get(reverse('portfolio:edit_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}))
        self.assertEqual(response.status_code, 403)

    def test_logged_user_owner(self):
        """
        Logged user who is the owner of the edit_project requested profile is redirected
        to the edit_project page.
        """
        response = self.client.post('/signin/', {'username': 'Test', 'password': 'testpassword'})
        response = self.client.get(reverse('portfolio:edit_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}))
        self.assertEqual(response.status_code, 200)
    
    def test_project_updated(self):
        """
        The Project instance has its data updated.
        """
        self.assertEqual(self.portfoller_project.project_name, 'Test_project')
        response = self.client.post('/signin/', {'username': 'Test', 'password': 'testpassword'})
        response = self.client.post(reverse('portfolio:edit_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}), data={
            'project_name': 'Updated', 'project_description': 'This is a test project updated description.', 'projectimages_set-TOTAL_FORMS': 1,
            'projectimages_set-INITIAL_FORMS': 0, 'projectimages_set-MIN_NUM_FORMS': 0, 'projectimages_set-MAX_NUM_FORMS': 30})
        self.portfoller_project.refresh_from_db()
        self.assertEqual(self.portfoller_project.project_name, 'Updated')      

class DeleteProjectViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portfoller = create_portfoller('Test')
        cls.portfoller_project = create_project(cls.portfoller, 'Test_project', 'Test_description')
        cls.portfoller2 = create_portfoller('Test2')
        cls.sign_in_url = reverse('portfolio:signin') + '?next=' + reverse('portfolio:delete_project', kwargs={'username': cls.portfoller.username, 'project_name': cls.portfoller_project.project_name})

    def test_not_logged_user_not_owner(self):
        """
        Not logged user are redirected to sign in page and if it don't sign in the delete_project
        requested profile, a `PermissionDenied` error is raised.
        """
        response = self.client.get(reverse('portfolio:delete_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}), follow=True)
        self.assertRedirects(response, self.sign_in_url)
        response = self.client.post(self.sign_in_url, {'username': 'Test2', 'password': 'testpassword'}, follow=True)
        self.assertEqual(response.status_code, 403)
    
    def test_not_logged_user_owner(self):
        """
        Not logged user are redirected to sign in page and if it sign in the delete_project
        requested profile, it's redirected to the delete_project page.
        """
        response = self.client.get(reverse('portfolio:delete_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}), follow=True)
        self.assertRedirects(response, self.sign_in_url)
        response = self.client.post(self.sign_in_url, {'username': 'Test', 'password': 'testpassword'}, follow=True)
        self.assertRedirects(response, reverse('portfolio:delete_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}))

    def test_logged_user_not_owner(self):
        """
        Logged user who is not the owner of the delete_project requested profile raises a
        `PermissionDenied` error.
        """ 
        response = self.client.post('/signin/', {'username': 'Test2', 'password': 'testpassword'})
        response = self.client.get(reverse('portfolio:delete_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}))
        self.assertEqual(response.status_code, 403)

    def test_logged_user_owner(self):
        """
        Logged user who is the owner of the delete_project requested profile is redirected
        to the delete_project page.
        """
        response = self.client.post('/signin/', {'username': 'Test', 'password': 'testpassword'})
        response = self.client.get(reverse('portfolio:delete_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}))
        self.assertEqual(response.status_code, 200)
    
    def test_project_deleted(self):
        """
        The Project instance is deleted.
        """
        self.assertEqual(Project.objects.filter(user=self.portfoller).count(), 1)
        response = self.client.post('/signin/', {'username': 'Test', 'password': 'testpassword'})
        response = self.client.post(reverse('portfolio:delete_project', kwargs={'username': self.portfoller.username, 'project_name': self.portfoller_project.project_name}))
        self.assertEqual(Project.objects.filter(user=self.portfoller).count(), 0)

class SignUpViewTests(TestCase):
    def test_portfoller_created_and_logged(self):
        """
        The Portfoller instance is created after sign up and the user is logged in the signed up user account.
        """
        self.assertEqual(Portfoller.objects.count(), 0)
        with open(os.getcwd() + '/portfoling\media/test_media/test_image.png', 'rb') as profile_picture:
            response = self.client.post('/signup/', data={
                'profile_picture': profile_picture, 'username': 'test_portfoller', 'first_name': 'Test',
                'last_name': 'Test', 'gender': 'Male', 'birthdate': '2000-01-01', 'country_of_birth': 'BR',
                'career': 'Developer', 'biography': 'test_biography', 'email': 'testmail@testmail.com',
                'password1': 'complicatedpasswordtopassvalidation', 'password2': 'complicatedpasswordtopassvalidation'})
        self.assertEqual(Portfoller.objects.count(), 1)
        self.assertEqual(int(self.client.session['_auth_user_id']), Portfoller.objects.get(username='test_portfoller').id)

class SignInViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portfoller = create_portfoller('Test')

    def test_correct_password(self):
        """
        The user is logged in if it passes the correct username and password in the sign-in form.
        """
        response = self.client.post('/signin/', data={'username':'Test', 'password': 'testpassword'})
        self.assertEqual(int(self.client.session['_auth_user_id']), Portfoller.objects.get(username='Test').id)

    def test_incorrect_password(self):
        """
        The user is not logged in if it passes the incorrect password in the sign-in form.
        """
        try:
            response = self.client.post('/signin/', data={'username':'Test', 'password': 'testwrongpassword'})
            self.assertEqual(int(self.client.session['_auth_user_id']), Portfoller.objects.get(username='Test').id)
        except KeyError:
            self.assertRaises(KeyError)

class SignOutViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portfoller = create_portfoller('Test')
    
    def test_user_is_logget_out(self):
        """
        The user is logged out successfully
        """
        response = self.client.post('/signin/', {'username': 'Test', 'password': 'testpassword'})
        self.assertEqual(int(self.client.session['_auth_user_id']), Portfoller.objects.get(username='Test').id)
        response = self.client.post('/signout/')
        try:
            self.assertEqual(int(self.client.session['_auth_user_id']), Portfoller.objects.get(username='Test').id)
        except KeyError:
            self.assertRaises(KeyError)

