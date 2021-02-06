from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = pages_list

    # Return a rendered response to send to the client
    return render(request, 'rango/index.html', context=context_dict)


def about(request):

    return render(request, 'rango/about.html')


def show_category(request, category_name_slug):
    # Create a context dictionary for the template rendering engine
    context_dict = {}

    try:
        # if the cateogry name slug does not exist the .get() method raises an exception
        # if it does exist, then it returns a model instance
        category = Category.objects.get(slug=category_name_slug)

        # retrieve all the associated pages
        pages = Page.objects.filter(category=category)

        # add the pages to the context dict
        context_dict['pages'] = pages
        # add the category (it will help in the template)
        context_dict['category'] = category
    except Category.DoesNotExist:
        # if there is no category, we just set the values to null
        # the template will render a 'no category' message
        context_dict['category'] = None
        context_dict['page'] = None

    return render(request, 'rango/category.html', context=context_dict)


def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)
            return redirect('/rango/')
        else:
            # the form contained errors, print them to the terminal
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug': category_name_slug}))

        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)
