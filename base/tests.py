from rest_framework import status
from django.test import TestCase
from .models import Topic,User
from rest_framework.test import APITestCase
from django.urls import reverse

# Create your tests here.
class Firsttestcase(TestCase):

    def test_Topic(self):

        Topics = ['blockchain','web3','springboot']

        for topic in Topics:
            obj = Topic.objects.create(
                name = topic
            )

            self.assertEqual(topic,obj.name)

        objs = Topic.objects.all()
        self.assertEqual(objs.count(),3)

class Accounttest(APITestCase):

    def test_register(self):
        _data = {
            "name" : "testcase",
            "username" : "testcase123",
            "email" : "testcase123@gmail.com",
            "password" : "ANzy12345.COM"
        }
        url = reverse("register")
        _response = self.client.post(url,data=_data,format="json")
        _data = _response.json()
        self.assertTrue(User.objects.filter(username="zyan123").exists())



