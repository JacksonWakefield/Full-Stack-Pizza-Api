from django.db import models

# Create your models here.

class Toppings(models.Model):
    name = models.CharField(max_length=100, unique=True, primary_key=True)

    def __str__(self):
        return self.name