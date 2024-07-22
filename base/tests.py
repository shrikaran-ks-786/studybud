from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model  # Import get_user_model
from django.contrib.auth.hashers import make_password

from .models import Room, Topic, Message  # Adjust import path based on your project structure
from .forms import RoomForm, NewTopicForm, Myusercreationform  # Adjust import path based on your project structure
from .views import Loginpage, Registeruser, home, room  # Import views to be tested

User = get_user_model()  # Get the custom user model


class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

        # Create a test user for authentication using custom user model
        self.test_user = User.objects.create(
            username='testuser',
            email='testuser@example.com',
            password=make_password('testpassword')
        )

    def test_login_page_GET(self):
        # Test GET request to login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login_register.html')

    def test_login_page_POST_valid_credentials(self):
        # Test POST request to login page with valid credentials
        login_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('home'))

    def test_login_page_POST_invalid_credentials(self):
        # Test POST request to login page with invalid credentials
        login_data = {
            'email': 'invaliduser@example.com',
            'password': 'invalidpassword',
        }
        response = self.client.post(reverse('login'), login_data, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'base/login_register.html')
        self.assertIn('username or password is incorrect', [msg.message for msg in response.context['messages']])

    def test_register_user_GET(self):
        # Test GET request to register page
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login_register.html')


    def test_register_user_POST_invalid_data(self):
    # Test POST request to register page with invalid data
        register_data = {
            'username': 'newuser',
            'email': 'invalidemail',  # Invalid email format
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(reverse('register'), register_data, follow=True)

        # Check that user is not authenticated
        self.assertFalse(response.context['user'].is_authenticated)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'base/login_register.html')

        # Check that the error message is present in the response messages
        error_messages = [msg.message for msg in response.context['messages']]
        self.assertIn('An error occurred during reg', error_messages)
