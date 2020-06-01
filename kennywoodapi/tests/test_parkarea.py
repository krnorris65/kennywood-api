import unittest
from django.test import TestCase
from django.urls import reverse
from kennywoodapi.models import ParkArea, Customer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Running your tests: https://docs.djangoproject.com/en/3.0/topics/testing/overview/#running-tests
# If I want to run all the tests: `python manage.py test`
# For the following commands, I will need to make sure I add this module to __init__.py
# If I want to run just this test class: `python manage.py test kennywoodapi.tests.TestParkAreas`
# If I want to run a single method in this class: `python manage.py test kennywoodapi.tests.TestParkAreas.testPostParkarea`


class TestParkAreas(TestCase):
    # Set up all data that will be needed to excute all the tests in the test file.
    def setUp(self):
        self.username = 'TestUser'
        self.password = 'Test123'
        self.user = User.objects.create_user(
            username=self.username, password=self.password)
        self.token = Token.objects.create(user=self.user)
        self.customer = Customer.objects.create(user_id=1, family_members=9)

    def test_post_parkarea(self):
        # Create a new park area
        new_parkarea = {
            "name": "Test Park Area",
            "theme": "Integration tests"
        }

        # Use the client to make the HTTP POST request and store the response
        response = self.client.post(
            reverse('parkarea-list'), new_parkarea, HTTP_AUTHORIZATION='Token ' + str(self.token)
        )

        # Assert: Does the status code of the HTTP response indicate that the it was successful?
        self.assertEqual(response.status_code, 200)

        # Query the table to see if there's one ParkArea instance in there. Since we are testing a POST request, we use the ORM to make sure the item was created in the database. Remember, the tests are run against a testing database that initially has no data.
        # Assert: Is there one new parkarea in the database?
        self.assertEqual(ParkArea.objects.count(), 1)

        # Assert: Is the parkarea in the database the one we just created?
        self.assertEqual(ParkArea.objects.get().name, new_parkarea["name"])

    def test_get_parkarea(self):
        new_parkarea = ParkArea.objects.create(
            name="Test Park Area",
            theme="Integration tests"
        )

        # Now we can grab all the parkareas (meaning the one we just created) from the db
        response = self.client.get(
            reverse('parkarea-list'), HTTP_AUTHORIZATION='Token ' + str(self.token))

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # There's just one product in our testing db, so our collection of parkareas that we get back as a response should have one parkarea.
        self.assertEqual(len(response.data), 1)
        # Remember, response.data is the Python serialized data used to render the JSON, while response.content is the JSON itself.

        # First, test the contents of the data before serialization
        self.assertEqual(response.data[0]["id"], 1)
        self.assertEqual(response.data[0]["name"], new_parkarea.name)

        # Then, test the actual rendered content as the client would receive it.
        # .encode converts from unicode to utf-8. Don't get hung up on this. It's just how we can compare apples to apples
        self.assertIn(new_parkarea.name.encode(), response.content)

    def test_delete_parkarea(self):
        new_parkarea = ParkArea.objects.create(
            name="Test Park Area",
            theme="Integration tests"
        )

        # Delete a parkarea. As shown in our post and get tests above, new_parkarea
        # will be the only parkarea in the database, and will have an id of 1
        response = self.client.delete(
            reverse('parkarea-detail', kwargs={'pk': 1}), HTTP_AUTHORIZATION='Token ' + str(self.token))

        # Check that the response is 204.
        self.assertEqual(response.status_code, 204)

        # Confirm that the parkarea is NOT in the database, which means there is nothing in the parkarea table.
        response = self.client.get(
            reverse('parkarea-list'), HTTP_AUTHORIZATION='Token ' + str(self.token))
        self.assertEqual(len(response.data), 0)

    def test_edit_parkarea(self):
        new_parkarea = ParkArea.objects.create(
            name="Test Park Area",
            theme="Integration tests"
        )

        # Create new updated parkare.
        updated_parkarea = {
            "name": "Updated Test Park Area",
            "theme": "Integration tests"
        }

        # Update the parkarea in the db
        response = self.client.put(
            reverse('parkarea-detail', kwargs={'pk': 1}),
            updated_parkarea,
            content_type='application/json',
            HTTP_AUTHORIZATION='Token ' + str(self.token)
        )

        # Assert that the PUT returns the expected 204 status
        self.assertEqual(response.status_code, 204)

        # Get the parkarea again, it should now be the updated parkarea.
        response = self.client.get(
            reverse('parkarea-detail', kwargs={'pk': 1}), HTTP_AUTHORIZATION='Token ' + str(self.token)
        )

        # Assert that the name has been updated
        self.assertEqual(response.data["name"], updated_parkarea["name"])


if __name__ == '__main__':
    unittest.main()
