from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from .models import Room,Topic,Message,User
from .forms import RoomForm,NewTopicForm,Myusercreationform
from rest_framework import status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
import os
from groq import Groq

client = Groq(
    api_key="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",
)


def Loginpage(request):

    page = "login"

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request,"user does not exist")
        
        user = authenticate(request,email=email,password=password)
        
        if user is not None:
            login(request,user)
            return redirect("home")
        else:
            messages.error(request,"username or password is incorrect")

    context = {"page" : page}
    return render(request,"base/login_register.html",context)

def Logoutpage(request):
    logout(request)
    return redirect("home")

def Registeruser(request):
    form = Myusercreationform()
    if request.method == "POST":
        form = Myusercreationform(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect("home")
            # return Response({"data": {}, "status": True, "message": "Your account is created"}, status=status.HTTP_201_CREATED)

        else:
            messages.error(request,"An error occurred during reg")
            # return Response({"data": {}, "status": False, "message": "Your account is not created"}, status=status.HTTP_400_BAD_REQUEST)



    return render(request,"base/login_register.html",{"form" : form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') !=None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q))
    room_count = rooms.count()

    for room in rooms:
        room.is_host = (request.user == room.host) 

    topics = Topic.objects.all()
    context = {"rooms":rooms,"topics" : topics,"room_count" : room_count}
    return render(request,"base/home.html",context)

# # def room(request,pk):
#     room = Room.objects.get(id=pk)
#     msg = room.message_set.all().order_by("-created")
#     participants = room.participants.all()

#     for m in msg:
#         m.is_host = (request.user == m.user) 

#     if request.method == "POST":
#         roommsg = Message.objects.create(
#             user=request.user,
#             room=room,
#             body=request.POST.get('body')
#         )
#         room.participants.add(request.user)
#         print(settings.EMAIL_HOST_USER,room.host.email)

#         if room.host.email:
#             subject = 'this email is from django server'
#             message = 'this is a test email'
#             from_email = settings.EMAIL_HOST_USER
#             recipient_list = ["shrikaranks@gmail.com"]
#             send_mail(subject, message, from_email, recipient_list)

#         return redirect('room',pk=room.id)
#     context = {"room" : room,"roommessages" : msg,"participants":participants}
#     return render(request,"base/room.html",context)

@login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    msg = room.message_set.all().order_by("-created")
    participants = room.participants.all()

    for m in msg:
        m.is_host = (request.user == m.user)

    if request.method == "POST":
        roommsg = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        print(settings.EMAIL_HOST_USER, room.host.email)

        # Check if the number of comments is a multiple of 2
        if msg.count() % 2 == 0 and msg.count() >= 2:
            # Retrieve the last two comments
            last_two_comments = msg[:2]

            # Generate a summary using Groq
            summary = generate_summary(last_two_comments)

            # Send summary via email to room host
            send_summary_to_host(summary, room.host.email)

        return redirect('room', pk=room.id)
    
    context = {"room": room, "roommessages": msg, "participants": participants}
    return render(request, "base/room.html", context)


def generate_summary(comments):
    # Function to generate a summary using Groq
    # Example implementation, modify as per your Groq usage
    content = "\n".join(comment.body for comment in comments)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": f"Please provide a short summary of:\n{content}"}
        ],
        model="llama3-8b-8192",
    )
    # Assuming Groq returns a summary
    summary = chat_completion.choices[0].message.content
    return summary


def send_summary_to_host(summary, host_email):
    # Function to send summary via email
    subject = 'Summary of Recent Comments'
    message = summary
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [host_email]
    send_mail(subject, message, from_email, recipient_list)



@login_required(login_url='login')
def createRoom(request):
    if request.method == 'POST':
        room_form = RoomForm(request.POST)
        new_topic_form = NewTopicForm(request.POST)

        if room_form.is_valid():
            room = room_form.save(commit=False)
            room.host = request.user
            room.save()

            # If a new topic is provided, create a new Topic object
            if new_topic_form.is_valid() and new_topic_form.cleaned_data['new_topic']:
                new_topic_name = new_topic_form.cleaned_data['new_topic']
                # Assuming you have a Topic model and a 'name' field
                new_topic = Topic.objects.create(name=new_topic_name)
                room.topic = new_topic
                room.save()

            messages.success(request, 'Room created successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Error creating room.')

    else:
        room_form = RoomForm()
        new_topic_form = NewTopicForm()

    context = {
        'room_form': room_form,
        'new_topic_form': new_topic_form,
    }
    return render(request, 'base/room_form.html', context)

    

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("ur not allowed to delete this")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request,"base/delete.html",{"obj" : room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    chat = Message.objects.get(id=pk)

    if request.user != chat.user:
        return HttpResponse("ur not allowed to delete this")

    if request.method == "POST":
        chat.delete()
        return redirect("home")
    return render(request,"base/delete.html",{"obj" : chat})





