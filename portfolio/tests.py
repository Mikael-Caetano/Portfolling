from django.urls import reverse
from django.test import TestCase

from .models import *

def create_portfoller(username, first_name=None, last_name=None, email=None, password='testpassword', gender='Male', birthdate='2000-01-01', country_of_birth='BR', career='Developer', biography=None):
    """
    Create a portfoller with the given `username` and `password`, and gives it
    all the other fields information.
    """
    first_name = username
    last_name = username
    email = username + '@testmail.com'
    return Portfoller.objects.create(username=username, password=password, first_name=first_name,
    last_name=last_name, gender=gender, birthdate=birthdate, country_of_birth=country_of_birth,
    career=career, email=email, biography=biography)

def create_multi_portfoller(n):
    """
    Create `n` portfollers with a autogenerate username and
    password, and gives it all the other fields information.
    """
    portfollers = []
    for x in range(n):
        username = 'test' + str(x)
        porfoller = create_portfoller(username=username)
        portfollers.append(portfoller)
    return portfollers

def create_project(portfoller, project_name, project_description):
    """
    Create a project with the given `project_name` and 
    `project_description` to the given `portfoller`.
    """
    return Project.objects.create(user=portfoller, project_name=project_name, project_description=project_description)

class PortfollerIndexViewTests(TestCase):
    def test_no_portfollers(self):
        """
        If no portfollers exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Portfollers are available.")
        self.assertQuerysetEqual(response.context['portfoller_list'], [])

    def test_one_portfoller(self):
        """
        Existent user is shown in the home page.
        """

        portfoller_1 = create_portfoller('test1')
        response = self.client.get(reverse('portfolio:home'))
        self.assertQuerysetEqual(
            response.context['portfoller_list'],
            ['<Portfoller: test1 test1>']
        )

    def test_four_portfollers(self):
        """
        Existent users are shown in the home page.
        """
        portfollers = create_multi_portfoller(4)
        response = self.client.get(reverse('portfolio:home'))
        self.assertQuerysetEqual(
            response.context['portfoller_list'],
            ['<Portfoller: test1 test1>', '<Portfoller: test2 test2>', '<Portfoller: test3 test3>', '<Portfoller: test4 test4>']
        )




# class QuestionDetailViewTests(TestCase):
#     def test_future_question(self):
#         """
#         The detail view of a question with a pub_date in the future
#         returns a 404 not found.
#         """
#         future_question = create_question(question_text='Future question.', days=5)
#         url = reverse('polls:detail', args=(future_question.id,))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 404)

#     def test_past_question(self):
#         """
#         The detail view of a question with a pub_date in the past
#         displays the question's text.
#         """
#         past_question = create_question(question_text='Past Question.', days=-5)
#         url = reverse('polls:detail', args=(past_question.id,))
#         response = self.client.get(url)
#         self.assertContains(response, past_question.question_text)

# class QuestionResultsViewTests(TestCase):
#     def test_future_question(self):
#         """
#         The results view of a question with a pub_date in the future
#         returns a 404 not found.
#         """  
#         future_question = create_question(question_text='Future question.', days=5)
#         url = reverse('polls:detail', args=(future_question.id,))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 404)

#     def test_past_question(self):
#         """
#         The results view of a question with a pub_date in the past
#         displays the question's results.
#         """       
#         past_question = create_question(question_text='Past Question', days= -5)
#         past_choice = create_choice(question=past_question, choice_text='Past Choice')
#         url = reverse('polls:detail', args=(past_question.id,))
#         response = self.client.get(url)
#         self.assertContains(response, past_question.question_text)
#         self.assertContains(response, past_choice.votes)
