from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import MoneyRequest

from moneyrequest.serializers import (
    MoneyRequestSerializer,
    MoneyRequestDetailSerializer,
)

MONEYREQUEST_URL = 'moneyrequest:moneyrequest-list'


def detail_url(moneyrequest_id):
    '''Return money request detail URL'''
    return reverse('moneyrequest:moneyrequest-detail', args=[moneyrequest_id])


def create_moneyrequest(borrower, **params):
    '''Helper function to create a money request'''
    defaults = {
        'title': 'Test title',
        'description': 'Test description',
        'amount': Decimal('777.77'),
        'frequency': 'WEEKLY',
        'term': 7,
    }
    defaults.update(params)

    moneyquest = MoneyRequest.objects.create(borrower=borrower, **defaults)
    return moneyquest


def create_borrower(**params):
    '''Helper function to create a borrower'''
    return get_user_model().objects.create_user(**params) # type: ignore


def create_lender(**params):
    '''Helper function to create a lender'''
    return get_user_model().objects.create_user(**params) # type: ignore


class PublicMoneyRequestApiTests(TestCase):
    '''Test the public money request API'''
    def setUp(self):
        '''Set up the test environment'''
        self.client = APIClient()

    def test_auth_required(self):
        '''Test that authentication is required'''
        res = self.client.get(reverse(MONEYREQUEST_URL))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMoneyRequestApiTests(TestCase):
    '''Test the private money request API'''
    def setUp(self):
        '''Set up the test environment'''
        self.client = APIClient()
        self.borrower = create_borrower(
            email='test@testing.com',
            password='testing*123',
        )
        self.client.force_authenticate(self.borrower)

    def test_retrieve_moneyrequests(self):
        '''Test retrieving a list of money requests'''
        create_moneyrequest(borrower=self.borrower)
        create_moneyrequest(borrower=self.borrower)

        res = self.client.get(reverse(MONEYREQUEST_URL))

        moneyrequests = MoneyRequest.objects.all().order_by('-id')
        serializer = MoneyRequestSerializer(moneyrequests, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data) # type: ignore

    def test_moneyrequests_limited_to_user(self):
        '''Test that money requests are limited to the authenticated user'''
        borrower2 = create_borrower(
            email='othertest@testing.com',
            password='testing*123',
        )
        create_moneyrequest(borrower=borrower2)
        create_moneyrequest(borrower=self.borrower)

        res = self.client.get(reverse(MONEYREQUEST_URL))

        moneyrequests = MoneyRequest.objects.filter(borrower=self.borrower)
        serializer = MoneyRequestSerializer(moneyrequests, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1) # type: ignore
        self.assertEqual(res.data, serializer.data) # type: ignore

    def test_view_moneyrequest_detail(self):
        '''Test viewing a money request detail'''
        moneyrequest = create_moneyrequest(borrower=self.borrower)

        url = detail_url(moneyrequest.id) # type: ignore
        res = self.client.get(url)

        serializer = MoneyRequestDetailSerializer(moneyrequest)
        self.assertEqual(res.data, serializer.data) # type: ignore

    def test_create_basic_moneyrequest(self):
        '''Test creating a money request'''
        payload = {
            'title': 'Test title',
            'description': 'Test description',
            'amount': Decimal('777.77'),
            'frequency': 'WEEKLY',
            'term': 7,
        }
        res = self.client.post(reverse(MONEYREQUEST_URL), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        moneyrequest = MoneyRequest.objects.get(id=res.data['id']) # type: ignore
        for k,v in payload.items():
            self.assertEqual(getattr(moneyrequest, k), v)
        self.assertEqual(moneyrequest.borrower, self.borrower)

    def test_partial_update_moneyrequest(self):
        '''Test updating a money request with patch'''
        moneyrequest = create_moneyrequest(borrower=self.borrower)

        payload = {'title': 'New title'}
        url = detail_url(moneyrequest.id) # type: ignore
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        moneyrequest.refresh_from_db()
        self.assertEqual(moneyrequest.title, payload['title'])
        self.assertEqual(moneyrequest.borrower, self.borrower)
        self.assertEqual(moneyrequest.amount, Decimal('777.77'))
        self.assertEqual(moneyrequest.frequency, 'WEEKLY')
        self.assertEqual(moneyrequest.term, 7)

    def test_full_update_moneyrequest(self):
        '''Test updating a money request with put'''
        moneyrequest = create_moneyrequest(borrower=self.borrower)

        payload = {
            'title': 'New title',
            'description': 'New description',
            'amount': Decimal('888.88'),
            'frequency': 'MONTHLY',
            'term': 12,
        }
        url = detail_url(moneyrequest.id) # type: ignore
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        moneyrequest.refresh_from_db()
        for k,v in payload.items():
            self.assertEqual(getattr(moneyrequest, k), v)
        self.assertEqual(moneyrequest.borrower, self.borrower)

    def test_update_moneyrequest_return_error(self):
        '''Test updating a money request user field returns an error'''
        new_borrower = create_borrower(
            email='newborrower@borrow.com',
            password='borrow*123',
        )
        moneyrequest = create_moneyrequest(borrower=self.borrower)

        payload = {'borrower': new_borrower.id} # type: ignore
        url = detail_url(moneyrequest.id) # type: ignore
        self.client.patch(url, payload)

        moneyrequest.refresh_from_db()
        self.assertEqual(moneyrequest.borrower, self.borrower)
        self.assertNotEqual(moneyrequest.borrower, new_borrower)

    def test_delete_moneyrequest(self):
        '''Test deleting a money request'''
        moneyrequest = create_moneyrequest(borrower=self.borrower)

        url = detail_url(moneyrequest.id) # type: ignore
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MoneyRequest.objects.count(), 0)

    def test_delete_other_moneyrequest(self):
        '''Test deleting another user's money request'''
        new_borrower = create_borrower(
            email='newborrower@borrow.com',
            password='borrow*123',
        )
        moneyrequest = create_moneyrequest(borrower=new_borrower)

        url = detail_url(moneyrequest.id) # type: ignore
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(MoneyRequest.objects.count(), 1)