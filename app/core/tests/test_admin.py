from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTests(TestCase):
    '''Test the admin site'''
    def setUp(self):
        '''Set up the test environment'''
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser( # type: ignore
            email='admin@testing.com',
            password='testing*123',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user( # type: ignore
            email='user@testing.com',
            password='testing*123',
            name='Tester',
        )

    def test_users_listed(self):
        '''Test that users are listed on the user page'''
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_user_change_page(self):
        '''Test that the user edit page works'''
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        '''Test that the create user page works'''
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)