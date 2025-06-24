from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Food
from .forms import CreateUser
from django.utils import timezone
import requests

# Create your views here.

def signup_view(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            user = form.save()  # Fixed: called save() method
            login(request, user)
            return redirect('index')
    else:
        form = CreateUser()
    return render(request, 'c_app/signup.html', {'form': form})  # Fixed: 'rorm' ➜ 'form'

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'c_app/login.html', {'error': 'Invalid Credentials'})
    return render(request, 'c_app/login.html')

@login_required
def index(request):
    foods = Food.objects.filter(user=request.user, date_added=timezone.now().date())  # Fixed: .objects.filter
    total = sum(food.calories for food in foods)
    return render(request, 'c_app/index.html', {
        'foods': foods,
        'total_cals': total
    })

@login_required
def add_food(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            url = "https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                'search_terms': name,
                'search_simple': 1,
                'action': 'process',
                'json': 1
            }
            response = requests.get(url, params=params)
            try:
                product = response.json()['products'][0]
                calories = int(float(product.get('nutriments', {}).get('energy-kcal_100g', 0)))  # Fixed key
            except (KeyError, IndexError, ValueError):
                calories = 0

            Food.objects.create(user=request.user, name=name.title(), calories=calories)  # Fixed: .objects.create
    return redirect('index')

@login_required
def delete_food(request, food_id):
    Food.objects.get(id=food_id, user=request.user).delete()
    return redirect('index')

@login_required
def reset_day(request):
    Food.objects.filter(user=request.user, date_added=timezone.now().date()).delete()  # Fixed: filter instead of get
    return redirect('index')

def logout_view(request):
    logout(request)
    return redirect('login')
