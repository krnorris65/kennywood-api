import unittest
from django.test import TestCase
from django.urls import reverse
from kennywoodapi.models import ParkArea, Customer, Attraction
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class TestAttractions(TestCase):
    # Set up all data that will be needed to excute all the tests in the test file.
    def setUp(self):
        self.username = 'TestUser'
        self.password = 'Test123'
        self.user = User.objects.create_user(
            username=self.username, password=self.password)
        self.token = Token.objects.create(user=self.user)
        self.customer = Customer.objects.create(user_id=1, family_members=9)

        self.new_parkarea = ParkArea.objects.create(
            name="Test Park Area",
            theme="Integration tests"
        )
    
    def test_post_attraction(self):
        new_attraction = {
            'name': "Test Attraction",
            'area_id': self.new_parkarea.id
        }

        response = self.client.post(
            reverse('attraction-list'), new_attraction, HTTP_AUTHORIZATION='Token ' + str(self.token)
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Attraction.objects.count(), 1)

        self.assertEqual(Attraction.objects.get().name, new_attraction["name"])
        self.assertEqual(Attraction.objects.get().area.name, self.new_parkarea.name)
    
    def test_get_attraction(self):
        new_attraction = Attraction.objects.create(
            name="Test Attraction",
            area_id=self.new_parkarea.id
        )
        response = self.client.get(
            reverse('attraction-list'), HTTP_AUTHORIZATION='Token ' + str(self.token))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]["id"], 1)
        self.assertEqual(response.data[0]["name"], new_attraction.name)
        self.assertEqual(response.data[0]["area"]["name"], self.new_parkarea.name)

        self.assertIn(new_attraction.name.encode(), response.content)