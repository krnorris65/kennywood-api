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
        fields = ('id', 'url', 'attraction', 'starttime', 'attraction_id',)
        depth = 2      


class Itineraries(ViewSet):
    """Itineraries for Kennywood Amusement Park"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized Itinerary instance
        """
        customer = Customer.objects.get(user=request.auth.user)
        attraction = Attraction.objects.get(pk=request.data["attraction_id"])

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
            requesting_user = Customer.objects.get(user=request.auth.user)
            itinerary = Itinerary.objects.get(pk=pk)
            # only return the itinerary if the user requesting is the user that is associated with that itinerary
            if itinerary.customer == requesting_user:
                serializer = ItinerarySerializer(itinerary, context={'request': request})
                return Response(serializer.data)
            else: 
                return Response({}, status=status.HTTP_403_FORBIDDEN)
        except Exception as ex:
            return HttpResponseServerError(ex)
    
    def update(self, request, pk=None):
        """Handle PUT requests for an itinerary

        Return:
            Response -- Empty body with 204 status code
        """
        requesting_user = Customer.objects.get(user=request.auth.user)
        # only update the itinerary if the user requesting is the user that is associated with that itinerary
        itinerary = Itinerary.objects.get(pk=pk)
        if itinerary.customer == requesting_user:
            attraction = Attraction.objects.get(pk=request.data["attraction_id"])

            itinerary.attraction = attraction
            itinerary.starttime = request.data["starttime"]
            itinerary.save()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
        else: 
            return Response({}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single itinerary

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            requesting_user = Customer.objects.get(user=request.auth.user)
            itinerary = Itinerary.objects.get(pk=pk)
            # only delete the itinerary if the user requesting is the user that is associated with that itinerary
            if itinerary.customer == requesting_user:
                itinerary.delete()
            else: 
                return Response({}, status=status.HTTP_403_FORBIDDEN)
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
