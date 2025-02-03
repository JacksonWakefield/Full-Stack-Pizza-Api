from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Toppings
from .serializers import ToppingsSerializer

def index(request):

    toppings = Toppings.objects.all().values()

    return JsonResponse(list(toppings), safe=False)

@api_view(['POST'])
def createTopping(request):
        serializer = ToppingsSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['PUT']) # REMEMBER - PUT DECORATORS ON ALL
def updateTopping(request):
    try:
        # Get the old topping by its current name
        old_name = request.data.get("oldName")
        new_name = request.data.get("newName")

        print(f"oldName: {old_name}, newName: {new_name}")  # Add debugging output

        # Validate input
        if not old_name or not new_name:
            return Response({"error": "Both oldName and newName must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Find and update the topping
        newTopping = Toppings.objects.get(name=old_name)
        newTopping.name = new_name
        newTopping.save()

        # Return the updated name
        return Response({"name": newTopping.name}, status=status.HTTP_200_OK)
    except Toppings.DoesNotExist:
        # Handle case where topping is not found
        return Response({"error": "Topping not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # General error handling
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deleteTopping(request):

    try:
        name = request.data.get("name")
         # Filter and delete topping with the given name
        deleted_count, _ = Toppings.objects.filter(name=name).delete()

        if deleted_count == 0:
            return Response({"error": "Topping not found."}, status=status.HTTP_404_NOT_FOUND)

        print(f"{deleted_count} record(s) deleted successfully.")

        return Response({"Deleted topping with name: ": name}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error", str(e)}, status=status.HTTP_400_BAD_REQUEST)