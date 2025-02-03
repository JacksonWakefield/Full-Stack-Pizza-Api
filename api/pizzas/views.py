from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Pizza, PizzaToppings
from .serializers import PizzaSerializer, PizzaToppingsSerializer

from rest_framework.decorators import api_view

#READ
@api_view(['GET'])
def index(request):

    pizza = Pizza.objects.all().values()

    return JsonResponse(list(pizza), safe=False)

@api_view(['POST'])
def createPizza(request):
    serializer = PizzaSerializer(data=request.data)

    if(serializer.is_valid()):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['PUT']) # REMEMBER - PUT DECORATORS ON ALL
def updatePizza(request):
    try:
        # Get the old pizza by its current name
        old_name = request.data.get("oldName")
        new_name = request.data.get("newName")

        print(f"oldName: {old_name}, newName: {new_name}")  # Add debugging output

        # Validate input
        if not old_name or not new_name:
            return Response({"error": "Both oldName and newName must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Find and update the topping
        newPizza = Pizza.objects.get(name=old_name)
        newPizza.name = new_name
        newPizza.save()

        # Return the updated name
        return Response({"name": newPizza.name}, status=status.HTTP_200_OK)
    except Pizza.DoesNotExist:
        # Handle case where topping is not found
        return Response({"error": "Pizza not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # General error handling
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deletePizza(request):
    try:
        name = request.data.get("name")
         # Filter and delete topping with the given name
        deleted_count, _ = Pizza.objects.filter(name=name).delete()

        if deleted_count == 0:
            return Response({"error": "Pizza not found."}, status=status.HTTP_404_NOT_FOUND)

        print(f"{deleted_count} record(s) deleted successfully.")

        return Response({"Deleted pizza with name: ": name}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error", str(e)}, status=status.HTTP_400_BAD_REQUEST)

#returns a JSON with properly formatted pizza:topping key:value pairs
@api_view(['GET'])
def getPizzaToppings(request):
    try:
        pizzaToppings = list(PizzaToppings.objects.all().values())
        
        formattedPizzaTopping = []

        for toppingDict in pizzaToppings:
            currentKeys = [(e['pizzaName']) for e in formattedPizzaTopping]
            print(currentKeys)
            if toppingDict['pizzaName_id'] not in currentKeys:
                formTemp = {
                    'pizzaName': toppingDict['pizzaName_id'],
                    'toppings': [toppingDict['toppingName_id']]
                }
                formattedPizzaTopping.append(formTemp)
            else:
                newVal = next(filter(lambda pizza: pizza['pizzaName'] == toppingDict['pizzaName_id'], formattedPizzaTopping))
                newVal['toppings'].append(toppingDict['toppingName_id'])

        return JsonResponse(formattedPizzaTopping, safe=False)
    except Exception as e:
        print(str(e))
        return Response({"error", str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def createPizzaTopping(request):
    serializer = PizzaToppingsSerializer(data=request.data)

    if(serializer.is_valid()):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['DELETE'])
def deletePizzaTopping(request):
    try:
        # Get pizzaName and toppingName from the request
        pizza_name = request.data.get("pizzaName")
        topping_name = request.data.get("toppingName")

        if not pizza_name or not topping_name:
            return Response({"error": "Both pizzaName and toppingName are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a Pizza with the given pizza_name exists
        pizza = Pizza.objects.filter(name=pizza_name).first()

        if not pizza:
            return Response({"error": "Pizza not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the pizza already has a topping relation with the topping_name
        pizza_topping = PizzaToppings.objects.filter(pizzaName__name=pizza_name, toppingName__name=topping_name).first()

        if not pizza_topping:
            return Response({"error": "This topping is not associated with the pizza."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the PizzaTopping relationship
        pizza_topping.delete()

        return Response({"message": f"Topping '{topping_name}' removed successfully from pizza '{pizza_name}'."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
