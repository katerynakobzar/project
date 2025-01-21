from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm
import requests
from .models import SearchHistory
from django.contrib import messages
from django.urls import reverse
from decouple import config

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'weather/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main')
    else:
        form = AuthenticationForm()
    return render(request, 'weather/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect(reverse('main'))

def main(request):
    weather = None
    if request.method == 'POST':
        city = request.POST.get('city')
        api_key = config('API_KEY')
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        response = requests.get(url)
        data = response.json()

        if data.get('main'):
            weather = {
                'city': city,
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description']
            }
            # Збереження історії пошуку
            if request.user.is_authenticated:
                SearchHistory.objects.create(
                    user=request.user,
                    city=city,
                    temperature=weather['temperature'],
                    description=weather['description']
                )

    return render(request, 'weather/main.html', {'weather': weather})

def history(request):
    if request.user.is_authenticated:
        searches = SearchHistory.objects.filter(user=request.user).order_by('-search_date')
    else:
        searches = []
    return render(request, 'weather/history.html', {'searches': searches})



