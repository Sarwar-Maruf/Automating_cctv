from django.shortcuts import render, redirect
from .models import Category, Photo
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
import os
# Create your views here.




# @login_required(login_url='login')
def gallery(request):
    user = request.user
    category = request.GET.get('category')
    if category == None:
        photos = Photo.objects.filter(category__user=user)
    else:
        photos = Photo.objects.filter(
            category__name=category, category__user=user)

    categories = Category.objects.filter(user=user)
    context = {'categories': categories, 'photos': photos}
    return render(request, 'photos/gallery.html', context)


# @login_required(login_url='login')
def viewPhoto(request, pk):
    photo = Photo.objects.get(id=pk)
    return render(request, 'photos/photo.html', {'photo': photo})

def videos(request):
    folder_path = r'C:\\Users\\sarwa\\Desktop\\Third_EYE\\Third Eye Web - working with photos\\project\\project\\static\\human'
    filelinks = os.listdir(folder_path)
    links = {"filelinks": filelinks}
    return render(request, 'photos/videos.html', links)


# @login_required(login_url='login')
def addPhoto(request):
    user = request.user

    categories = user.category_set.all()

    if request.method == 'POST':
        data = request.POST
        images = request.FILES.getlist('images')
        print("hello:",type(images))

        if data['category'] != 'none':

            print("data:",data)
            print("data:",type(data))
            print("hele:",data['category'])
            category = Category.objects.get(id=data['category'])
            # print("catagori Id:", type(category))
        elif data['category_new'] != '':
            category, created = Category.objects.get_or_create(
                user=user,
                name=data['category_new'])
        else:
            category = None

        for image in images:
            photo = Photo.objects.create(
                category=category,
                description=data['description'],
                image=image,
            )

        return redirect('gallery')

    context = {'categories': categories}
    return render(request, 'photos/add.html', context)
