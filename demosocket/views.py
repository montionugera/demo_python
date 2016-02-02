from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import loader


def index(request):

    return render(request, 'demo_socket/index.html', {})

def client(request):

    return render(request, 'demo_socket/client.html', {})