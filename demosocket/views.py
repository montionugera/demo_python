import base64
import cStringIO
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import loader
import qrcode


def index(request):

    host_val = request.get_host()
    host_val = host_val.split(':')[0]
    return render(request, 'demo_socket/index.html', {'host_val':host_val})

def index2(request):

    host_val = request.get_host()
    host_val = host_val.split(':')[0]
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=80,
        border=1,
        )
    from random import randint
    room_id = randint(0,100000)
    qr.add_data("http://%s/demosocket/client/%s/"%(request.get_host(),room_id))
    qr.make(fit=True)
    img = qr.make_image()
    jpeg_image_buffer = cStringIO.StringIO()
    img.save(jpeg_image_buffer)
    base64qr_png = base64.b64encode(jpeg_image_buffer.getvalue())
    return render(request, 'demo_socket/index2.html', {'host_val':host_val,'base64qr_png':base64qr_png, 'room_id':room_id})

def index_all(request):

    host_val = request.get_host()
    host_val = host_val.split(':')[0]
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=80,
        border=1,
        )
    from random import randint
    room_id = 1
    qr.add_data("http://%s/demosocket/client/%s/"%(request.get_host(),room_id))
    qr.make(fit=True)
    img = qr.make_image()
    jpeg_image_buffer = cStringIO.StringIO()
    img.save(jpeg_image_buffer)
    base64qr_png = base64.b64encode(jpeg_image_buffer.getvalue())
    return render(request, 'demo_socket/index2.html', {'host_val':host_val,'base64qr_png':base64qr_png, 'room_id':room_id})

def client(request,room_id):
    host_val = request.get_host()
    host_val = host_val.split(':')[0]
    return render(request, 'demo_socket/client.html', {'host_val':host_val,'room_id':room_id})
