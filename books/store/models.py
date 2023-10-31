from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=250, null=True)

    def __str__(self):
        return f'{self.id}: {self.name}'