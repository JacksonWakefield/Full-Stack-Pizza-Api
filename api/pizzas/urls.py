from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.createPizza, name="create"),
    path("update/", views.updatePizza, name="update"),
    path("delete/", views.deletePizza, name="delete"),
    path("pizzatoppings/", views.getPizzaToppings, name="getPizzaToppings"),
    path("pizzatoppings/create/", views.createPizzaTopping, name="createPizzaTopping"),
    path("pizzatoppings/delete/", views.deletePizzaTopping, name="deletePizzaTopping"),
]