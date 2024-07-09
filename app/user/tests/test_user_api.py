from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')

def create_user(**params):
    '''Helper function to create a user'''
    return get_user_model().objects.create_user(**params) # type: ignore

class PublicUserApiTests(TestCase):
    '''Test the public users API'''
    def setUp(self):
        '''Set up the test environment'''
        self.client = APIClient()

    def test_create_valid_user_success(self):
        '''Test creating user with valid payload is successful'''
        payload = {
            'email': 'tester@testing.com',
            'password': 'testing*123',
            'name': 'Tester',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data) # type: ignore

    def test_user_exists(self):
        '''Test creating a user that already exists fails'''
        payload = {
            'email': 'tester@testing.com',
            'password': 'testing*123',
            'name': 'Tester',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        '''Test that the password cannot be too short'''
        payload = {
            'email': 'tester@testing.com',
            'password': 'pw',
            'name': 'Tester',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''Test that a token is created for the user'''
        user_details = {
            'email': 'test@testing.com',
            'password': 'testing*123',
            'name': 'Tester',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data) # type: ignore
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        '''Test that a token is not created for invalid credentials'''
        user_details = {
            'email': 'test@testing.com',
            'password': 'testing*123',
            'name': 'Tester',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': 'wrongpassword',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data) # type: ignore
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        '''Test that a token is not created for blank password'''
        payload = {
            'email': 'test@testing.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data) # type: ignore
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        '''Test that a token is not created for non-existent user'''
        payload = {
            'email': 'test@testing.com',
            'password': 'testing*123',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data) # type: ignore
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retreive_user_unauthorized(self):
        '''Test that authentication is required for users'''
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    '''Test API requests that require authentication'''
    def setUp(self):
        '''Set up the test environment'''
        self.user = create_user(
            email='test@testing.com',
            password='testing*123',
            name='Tester',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        '''Test retrieving profile for logged in user'''
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {  # type: ignore
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_profile_not_allowed(self):
        '''Test that POST is not allowed on the profile URL'''
        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        '''Test updating the user profile for authenticated user'''
        payload = {
            'name': 'new name',
            'password': 'newpassword*123',
        }
        res = self.client.patch(PROFILE_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)