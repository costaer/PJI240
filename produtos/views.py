# produtos/views.py

from django.shortcuts import render
from .models import Produto

def index(request):
    produtos = Produto.objects.all()
    return render(request, 'produtos/index.html', {'produtos': produtos})
