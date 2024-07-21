from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from .models import Room,Topic,Message,User
from .forms import RoomForm,NewTopicForm,Myusercreationform


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
        else:
            messages.error(request,"An error occured during reg")

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

def room(request,pk):
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
        return redirect('room',pk=room.id)
    context = {"room" : room,"roommessages" : msg,"participants":participants}
    return render(request,"base/room.html",context)


# @login_required(login_url='login')
# def createRoom(request):
#     if request.method == 'POST':
#         form = RoomForm(request.POST)
#         if form.is_valid():
#             room = form.save(commit=False)
#             room.host = request.user
#             room.save()
#             return redirect("home")
#     else:
#         form = RoomForm()
#         context = {"form" : form}
#         return render(request,'base/room_form.html',context)

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





