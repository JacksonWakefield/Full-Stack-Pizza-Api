from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Toppings
from .serializers import ToppingsSerializer

# /pizza - GET - returns copy of Toppings table from RDS
def index(request):
    # Retrieve all topping records and return as JSON
    toppings = Toppings.objects.all().values()
    return JsonResponse(list(toppings), safe=False)

# /pizza/create - POST - adds new Topping to RDS
@api_view(['POST'])
def createTopping(request):
    # Validate and save new topping
    serializer = ToppingsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

# /pizza/update - PUT - accepts old and new name of toppings, replaces old with new
# (note: I set the pizza's "name" as the pk - in a production environment this would never be the case)
@api_view(['PUT']) 
def updateTopping(request):
    try:
        old_name = request.data.get("oldName")
        new_name = request.data.get("newName")

        # Ensure both old and new names are provided
        if not old_name or not new_name:
            return Response({"error": "Both oldName and newName must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the topping name
        Toppings.objects.filter(name=old_name).update(name=new_name)

        return Response({"name": new_name}, status=status.HTTP_200_OK)
    except Toppings.DoesNotExist:
        return Response({"error": "Topping not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# /pizza/delete - DELETE - accepts name of topping, deletes topping with name from RDS
@api_view(['DELETE'])
def deleteTopping(request):
    try:
        name = request.data.get("name")

        # Delete topping with the given name
        deleted_count, _ = Toppings.objects.filter(name=name).delete()

        if deleted_count == 0:
            return Response({"error": "Topping not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"Deleted topping with name": name}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
