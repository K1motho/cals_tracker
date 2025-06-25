from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Food
from .forms import CreateUser
from django.utils import timezone
from django.db.models import Sum  # ✅ Required for annotation
import requests

# -----------------------
# USER AUTHENTICATION VIEWS
# -----------------------

def signup_view(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            print("seccesfuly logged in")
            return redirect('index')
    else:
        form = CreateUser()
    return render(request, 'signup.html', {'form': form})

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
            return render(request, 'login.html', {'error': 'Invalid Credentials'})
    print("seccesfuly logged in")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# -----------------------
# CORE FUNCTIONAL VIEWS
# -----------------------

@login_required
def index(request):
    today = timezone.now().date()
    foods = Food.objects.filter(user=request.user, date_added=today)
    total = sum(food.calories for food in foods)
    return render(request, 'index.html', {
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
                calories = int(float(product.get('nutriments', {}).get('energy-kcal_100g', 0)))
            except (KeyError, IndexError, ValueError):
                calories = 0

            Food.objects.create(user=request.user, name=name.title(), calories=calories)
    return redirect('index')

@login_required
def delete_food(request, food_id):
    Food.objects.filter(id=food_id, user=request.user).delete()
    return redirect('index')

@login_required
def reset_day(request):
    today = timezone.now().date()
    Food.objects.filter(user=request.user, date_added=today).delete()
    return redirect('index')

# -----------------------
# HISTORY VIEW
# -----------------------

@login_required
def history(request):
    history_data = (
        Food.objects
        .filter(user=request.user)
        .values('date_added')  
        .annotate(total_calories=Sum('calories'))  
        .order_by('-date_added')
    )
    return render(request, 'history.html', {'history': history_data})
