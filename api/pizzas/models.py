from django.db import models

from toppings.models import Toppings

# Create your models here.
class Pizza(models.Model):
    name = models.CharField(max_length=100, unique=True, primary_key=True)

    def __str__(self):
        return self.name

class PizzaToppings(models.Model):
    pizzaName = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    toppingName = models.ForeignKey(Toppings, on_delete=models.CASCADE)
