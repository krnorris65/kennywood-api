"""Itinery for Kennywood Amusement Park"""
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
        model: Itinerary
        url: serializers.HyperlinkedIdentityField(
            view_name="itinerary",
            lookup_field='id'
        )
        fields = ('id', 'url', 'customer', 'attraction', 'starttime')
    
    class Itinerary(ViewSet):
        """Itineraries for Kennywood Amusement Park"""

        def create(self, request):
            """Handle POST operations

            Returns:
                Response -- JSON serialized Itinerary instance
            """
            customer = Customer.objects.get(pk=request.auth.user)
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