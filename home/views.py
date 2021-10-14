from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request,'home/index.html')

def checkers(request):
    return render(request,'board.html')