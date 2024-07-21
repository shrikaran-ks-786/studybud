from django import forms
from .models import Room, Topic,User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

class Myusercreationform(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username','email','password1','password2']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
        exclude = ["host", "participants"]

class NewTopicForm(forms.Form):
    new_topic = forms.CharField(max_length=100, required=False)

