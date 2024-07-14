from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Account

from account.serializers import AccountSerializer

ACCOUNT_URL = 'account:account-list'


def detail_url(account_id):
    '''Return account detail URL'''
    return reverse('account:account-detail', args=[account_id])


def create_borrower(**params):
    '''Helper function to create a borrower'''
    return get_user_model().objects.create_user(**params) # type: ignore


def create_borrower_account(borrower, **params):
    '''Helper function to create an account'''
    defaults = {
        'type': 'BORROWER',
    }
    defaults.update(params)

    return Account.objects.create(user=borrower, **defaults)


def create_lender(**params):
    '''Helper function to create a lender'''
    return get_user_model().objects.create_user(**params) # type: ignore


def create_lender_account(lender, **params):
    '''Helper function to create an account'''
    defaults = {
        'type': 'LENDER',
    }
    defaults.update(params)

    return Account.objects.create(user=lender, **defaults)


class PublicAccountApiTests(TestCase):
    '''Test the public account API'''
    def setUp(self):
        '''Set up the test environment'''
        self.client = APIClient()


    def test_auth_required(self):
        '''Test that authentication is required'''
        res = self.client.get(reverse(ACCOUNT_URL))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAccountApiTests(TestCase):
    '''Test the private account API'''
    def setUp(self):
        '''Set up the test environment'''
        self.client = APIClient()
        self.borrower = create_borrower(
            email='borrower@testing.com',
            password='testing*123',
        )
        self.client.force_authenticate(self.borrower)


    def test_view_account(self):
        '''Test viewing account detail'''
        borrower_account = create_borrower_account(borrower=self.borrower)

        url = detail_url(borrower_account.id) # type: ignore
        res = self.client.get(url)

        serializer = AccountSerializer(borrower_account)
        self.assertEqual(res.data, serializer.data) # type: ignore


    def test_view_account_limited_to_user(self):
        '''Test viewing account for the authenticated user only'''
        borrower2 = create_borrower(
            email='otherborrower@testing.com',
            password='testing*123',
        )
        create_borrower_account(borrower=self.borrower)
        create_borrower_account(borrower=borrower2)

        res = self.client.get(reverse(ACCOUNT_URL))

        accounts = Account.objects.filter(user=self.borrower)
        serializer = AccountSerializer(accounts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1) # type: ignore
        self.assertEqual(res.data, serializer.data) # type: ignore


    def test_create_account(self):
        '''Test creating a new account'''
        payload = {
            'type': 'BORROWER',
        }
        res = self.client.post(reverse(ACCOUNT_URL), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        account = Account.objects.get(id=res.data['id']) # type: ignore
        self.assertEqual(account.user, self.borrower)


    def test_partial_update_account_return_error(self):
        '''Test updating an account with patch returns an error'''
        borrower_account = create_borrower_account(borrower=self.borrower)

        payload = {'balance': Decimal('888.66')}
        url = detail_url(borrower_account.id) # type: ignore
        self.client.patch(url, payload)

        borrower_account.refresh_from_db()
        self.assertNotEqual(borrower_account.balance, Decimal('888.66'))


    def test_change_account_type_return_error(self):
        '''Test updating an account type returns an error'''
        borrower_account = create_borrower_account(borrower=self.borrower)

        payload = {'type': 'LENDER'}
        url = detail_url(borrower_account.id) # type: ignore
        self.client.patch(url, payload)

        borrower_account.refresh_from_db()
        self.assertNotEqual(borrower_account.type, 'LENDER')


    def test_full_update_account_return_error(self):
        '''Test updating an account with put returns an error'''
        borrower_account = create_borrower_account(borrower=self.borrower)

        payload = {
            'type': 'LENDER',
            'balance': Decimal('888.66'),
        }
        url = detail_url(borrower_account.id) # type: ignore
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        borrower_account.refresh_from_db()
        self.assertNotEqual(borrower_account.type, 'LENDER')
        self.assertNotEqual(borrower_account.balance, Decimal('888.66'))


    def test_delete_account_return_error(self):
        '''Test deleting an account returns an error'''
        borrower_account = create_borrower_account(borrower=self.borrower)

        url = detail_url(borrower_account.id) # type: ignore
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Account.objects.count(), 1)