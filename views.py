from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from.models import Food
from .forms import CreateUser
from django.utils import timezone
import requests

# Create your views here.
def signup_view(request):
    if request.method == 'POST':
        form= CreateUser(request.POST)
        if form.is_valid():
            user= form.save
            login(request, user)
            return redirect('index')
    else :
        form = CreateUser()
    return render(request, 'c_app/signup.html', {'rorm': form})

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user :
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'c_app/login.html',{'error': 'Invalid Credentials'})
    return render (request, 'c_app/login.html')

def index(request):
    foods= Food.object.Filter(user=request.user, date_added=timezone.now().date())
    total = sum(food.calories for food in foods)
    return render (request, 'c_app/index.html',{
        'foods': foods,
        'total_cals': total
    })

def add_food(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name :
            url= f"https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                'search_terms': name,
                'search_simple': 1,
                'action': 'process',
                'json': 1.
            }
            response= requests.get(url, params=params)
            try:
                product = response.json()['products'][0]
                calories = int(float(product.get('nutrients',{}).get('energy-kal_100g',0)))
            except (KeyError, IndexError, ValueError):
                calories= 0

            Food.object.create(user= request.user, name=name.title(), calories=calories)
    return redirect('index')

def delete_food(request, food_id):
    Food.objects.get(id=food_id, user=request.user).delete()
    return redirect('index')

def reset_day(request):
    Food.objects.get(user=request.user, date_added=timezone.now().date()).delete()
    return redirect('index')

def logout_view(request):
    logout(request)
    return redirect('login')