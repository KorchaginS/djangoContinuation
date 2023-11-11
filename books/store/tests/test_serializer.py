from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):

    def test_serialization(self):
        # Сначала сериализируем объекты тестируемым сериализатором

        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        user3 = User.objects.create(username='user3')

        book_1 = Book.objects.create(name='Test book 1', price='25', author_name = 'Author 1')
        book_2 = Book.objects.create(name='Test book 2', price='75', author_name = 'Author 2')

        UserBookRelation.objects.create(user=user1, book=book_1, like=True)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True)
        UserBookRelation.objects.create(user=user3, book=book_1, like=True)

        UserBookRelation.objects.create(user=user1, book=book_2, like=True)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))).order_by('id')

        serializer_data = BooksSerializer(books, many=True).data

        # Потом собираем ожидаемый результат в коде руками
        expected_data = [
            {
                'id': book_1.id,
                'name':'Test book 1',
                'price':'25.00',
                'author_name' : 'Author 1',
                'likes_count': 3,
                'annotated_likes': 3
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '75.00',
                'author_name': 'Author 2',
                'likes_count': 2,
                'annotated_likes': 2
            }
        ]
        # Сравниваем
        self.assertEqual(serializer_data, expected_data)

