from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import loader


def index(request):

    host_val = request.get_host()
    host_val = host_val.split(':')[0]
    return render(request, 'demo_socket/index.html', {'host_val':host_val})

def client(request):
    host_val = request.get_host()
    host_val = host_val.split(':')[0]
    return render(request, 'demo_socket/client.html', {'host_val':host_val})