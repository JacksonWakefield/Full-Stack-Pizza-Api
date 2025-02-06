from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Pizza, PizzaToppings
from .serializers import PizzaSerializer, PizzaToppingsSerializer

# /pizza - GET - Returns list of pizzas from RDS
@api_view(['GET'])
def index(request):
    pizzas = Pizza.objects.all().values()
    return JsonResponse(list(pizzas), safe=False)

# /pizza/create - POST - Adds a new pizza to RDS
@api_view(['POST'])
def createPizza(request):
    serializer = PizzaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

# /pizza/update - PUT - Updates pizza name in RDS
@api_view(['PUT'])
def updatePizza(request):
    try:
        old_name = request.data.get("oldName")
        new_name = request.data.get("newName")

        # Validate input
        if not old_name or not new_name:
            return Response({"error": "Both oldName and newName must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the pizza exists
        pizza = Pizza.objects.filter(name=old_name).first()
        if not pizza:
            return Response({"error": "Pizza not found."}, status=status.HTTP_404_NOT_FOUND)

        # Start a database transaction to handle the update and related changes
        # Update the pizza name
        pizza.name = new_name
        pizza.save()

        # Update the associated PizzaToppings with the new pizza name
        PizzaToppings.objects.filter(pizzaName=pizza).update(pizzaName=new_name)

        return Response({"name": new_name}, status=status.HTTP_200_OK)
    except Pizza.DoesNotExist:
        return Response({"error": "Pizza not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# /pizza/delete - DELETE - Deletes a pizza by name from RDS
@api_view(['DELETE'])
def deletePizza(request):
    try:
        name = request.data.get("name")
        deleted_count, _ = Pizza.objects.filter(name=name).delete()

        if deleted_count == 0:
            return Response({"error": "Pizza not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"Deleted pizza with name": name}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# /pizza/toppings - GET - Returns formatted pizza:topping key:value pairs
# format is [{pizzaName:varchar, toppingName:varchar}]
@api_view(['GET'])
def getPizzaToppings(request):
    try:
        pizza_toppings = list(PizzaToppings.objects.all().values())
        formatted_pizza_toppings = []

        for topping_dict in pizza_toppings:
            current_keys = [entry['pizzaName'] for entry in formatted_pizza_toppings]

            if topping_dict['pizzaName_id'] not in current_keys:
                formatted_pizza_toppings.append({
                    'pizzaName': topping_dict['pizzaName_id'],
                    'toppings': [topping_dict['toppingName_id']]
                })
            else:
                entry = next(filter(lambda pizza: pizza['pizzaName'] == topping_dict['pizzaName_id'], formatted_pizza_toppings))
                entry['toppings'].append(topping_dict['toppingName_id'])

        return JsonResponse(formatted_pizza_toppings, safe=False)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# /pizza/toppings/create - POST - Adds a new pizza-topping relationship to RDS
@api_view(['POST'])
def createPizzaTopping(request):
    serializer = PizzaToppingsSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

# /pizza/toppings/delete - DELETE - Removes a topping from a pizza
@api_view(['DELETE'])
def deletePizzaTopping(request):
    try:
        pizza_name = request.data.get("pizzaName")
        topping_name = request.data.get("toppingName")

        # Validate input
        if not pizza_name or not topping_name:
            return Response({"error": "Both pizzaName and toppingName are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the pizza exists
        pizza = Pizza.objects.filter(name=pizza_name).first()

        if not pizza:
            return Response({"error": "Pizza not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the topping is associated with the pizza
        pizza_topping = PizzaToppings.objects.filter(pizzaName__name=pizza_name, toppingName__name=topping_name).first()

        if not pizza_topping:
            return Response({"error": "This topping is not associated with the pizza."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the pizza-topping relationship
        pizza_topping.delete()

        return Response({"message": f"Topping '{topping_name}' removed successfully from pizza '{pizza_name}'."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
