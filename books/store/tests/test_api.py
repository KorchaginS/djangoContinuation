import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test book 1', price='25', author_name='Author 1', owner = self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price='75', author_name='Author 5')
        self.book_3 = Book.objects.create(name='Test book Author 1', price='75', author_name='Author 2')

        UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True, rate=5)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        print(serializer_data)
        print('\n')
        print(response.data)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        #self.assertEqual(serializer_data[0]['likes_count'], 1)
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)


    def test_get_filter(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
            ).order_by('id')
        response = self.client.get(url, data={'price':75})

        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
            )
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
                "name": "Programmin in Python 3",
                "price": 150,
                "author_name": "Mark Summerfield"
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data = json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
                "name": self.book_1.name,
                "price": 575,
                "author_name": "Mark Summerfield"
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data = json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
                "name": self.book_1.name,
                "price": 575,
                "author_name": "Mark Summerfield"
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data = json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        print(response.data)
        self.book_1.refresh_from_db()
        self.assertEqual(25, self.book_1.price)


    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
                "name": self.book_1.name,
                "price": 575,
                "author_name": "Mark Summerfield"
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data = json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        print(response.data)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

class BooksRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Test book 1', price='25', author_name='Author 1', owner = self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price='75', author_name='Author 5')


    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            "like": True,

        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data= json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(relation.like, True)

        data = {
            "in_booksmark": True,
        }

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(relation.in_booksmark, True)


    def test_rating(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            "rate": 1,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data= json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(relation.rate, 1)

    def test_rating_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            "rate": 6,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(None, relation.rate)