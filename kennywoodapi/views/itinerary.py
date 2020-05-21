"""Itinerary for Kennywood Amusement Park"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from kennywoodapi.models import Itinerary, Attraction, Customer

class ItinerarySerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for park areas

    Arguments:
        serializers
    """
    class Meta:
        model = Itinerary
        url = serializers.HyperlinkedIdentityField(
            view_name="itinerary",
            lookup_field='id'
        )
        fields = ('id', 'url', 'attraction', 'starttime',)
        depth = 2      


class Itineraries(ViewSet):
    """Itineraries for Kennywood Amusement Park"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized Itinerary instance
        """
        customer = Customer.objects.get(user=request.auth.user)
        attraction = Attraction.objects.get(pk=request.data["ride_id"])

        new_itinerary = Itinerary()
        new_itinerary.customer = customer
        new_itinerary.attraction = attraction
        new_itinerary.starttime = request.data["starttime"]

        new_itinerary.save()

        serializer = ItinerarySerializer(new_itinerary, context={'request': request})

        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Handle GET requests for single itinerary

        Returns:
            Response -- JSON serialized itinerary instance
        """
        try:
            itinerary = Itinerary.objects.get(pk=pk)
            serializer = ItinerarySerializer(itinerary, context={'request': request})

            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)
    
    def update(self, request, pk=None):
        """Handle PUT requests for an itinerary

        Return:
            Response -- Empty body with 204 status code
        """
        attraction = Attraction.objects.get(pk=request.data["ride_id"])

        itinerary = Itinerary.objects.get(pk=pk)
        itinerary.attraction = attraction
        itinerary.starttime = request.data["starttime"]
        itinerary.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single itinerary

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            itinerary = Itinerary.objects.get(pk=pk)
            itinerary.delete()
        except Itinerary.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request):
        """Handle GET requests to itinerary resource

        Returns:
            Response -- JSON serialized list of itinerary
        """
        customer = Customer.objects.get(user=request.auth.user)

        itineraries = Itinerary.objects.filter(customer=customer)
        serializer = ItinerarySerializer(
            itineraries, many=True, context={'request': request})
        return Response(serializer.data)
