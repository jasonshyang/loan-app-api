from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

class ModelTests(TestCase):
    '''Test the user model'''
    def test_create_user_with_email_successful(self):
        '''Test creating a new user with an email is successful'''
        email = 'test@testing.com'
        password = 'testing*123'
        user = get_user_model().objects.create_user( # type: ignore
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        '''Test the email for a new user is normalized'''
        sample_email = [
            ['test1@TESTING.com', 'test1@testing.com'],
            ['Test2@TESTING.com', 'Test2@testing.com'],
            ['TEST3@Testing.com', 'TEST3@testing.com'],
        ]
        for email, normalized_email in sample_email:
            user = get_user_model().objects.create_user(email, 'testing*123') # type: ignore
            self.assertEqual(user.email, normalized_email)

    def test_new_user_invalid_email(self):
        '''Test creating user with no email raises error'''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testing*123') # type: ignore

    def test_create_new_superuser(self):
        '''Test creating a new superuser'''
        user = get_user_model().objects.create_superuser( # type: ignore
            'test@testing.com',
            'testing*123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_moneyrequest(self):
        '''Test creating a new money request'''
        borrower = get_user_model().objects.create_user( # type: ignore
            'borrower@testing.com',
            'testing*123',
        )
        money_request = models.MoneyRequest.objects.create(
            borrower=borrower,
            title='Test title',
            description='Test description',
            amount=Decimal('100.00'),
            frequency='WEEKLY',
            term=7,
        )

        self.assertEqual(str(money_request), money_request.title)

    def test_create_account(self):
        '''Test creating a new account'''
        borrower = get_user_model().objects.create_user( # type: ignore
            'borrower@testing.com',
            'testing*123',
        )
        borrow_account = models.Account.objects.create(
            user=borrower,
            type='BORROWER',
            balance=Decimal('100.00'),
        )

        self.assertEqual(str(borrow_account), borrow_account.user.email)

        lender = get_user_model().objects.create_user( # type: ignore
            'lender@testing.com',
            'testing*123',
        )
        lend_account = models.Account.objects.create(
            user=lender,
            type='LENDER',
            balance=Decimal('100.00'),
        )

        self.assertEqual(str(lend_account), lend_account.user.email)


