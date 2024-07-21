from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.Loginpage,name="login"),
    path('logout/',views.Logoutpage,name="logout"),
    path('register/',views.Registeruser,name="register"),
    path('',views.home,name="home"),
    path('room/<str:pk>/',views.room,name="room"),
    path('createroom',views.createRoom,name="createroom"),
    path('deleteroom/<str:pk>/',views.deleteRoom,name="deleteroom"),
    path('deletemessage/<str:pk>/',views.deleteMessage,name="deletemessage"),
]