from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    # Construct a dictionary to pass to the template engine as its context
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}

    # Return a rendered response to send to the client
    return render(request, 'rango/index.html', context=context_dict)


def about(request):

    return render(request, 'rango/about.html')
