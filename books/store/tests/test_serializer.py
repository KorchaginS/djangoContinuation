from django.test import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):

    def test_serialization(self):
        # Сначала сериализируем объекты тестируемым сериализатором
        book_1 = Book.objects.create(name='Test book 1', price='25', author_name = 'Author 1')
        book_2 = Book.objects.create(name='Test book 2', price='75', author_name = 'Author 2')

        serializer_data = BooksSerializer([book_1, book_2], many=True).data

        # Потом собираем ожидаемый результат в коде руками
        expected_data = [
            {
                'id': book_1.id,
                'name':'Test book 1',
                'price':'25.00',
                'author_name' : 'Author 1'
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '75.00',
                'author_name': 'Author 2'
            }
        ]
        # Сравниваем
        self.assertEqual(serializer_data, expected_data)

