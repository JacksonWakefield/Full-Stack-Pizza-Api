from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.createTopping, name="create"),
    path("update/", views.updateTopping, name="update"),
    path("delete/", views.deleteTopping, name="delete"),
]