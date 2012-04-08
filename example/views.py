# Create your views here.
from django.http import HttpResponse


def view_a(request):
    return HttpResponse('OK: A')


def view_b(request):
    return HttpResponse('OK: B')
