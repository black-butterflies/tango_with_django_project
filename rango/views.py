from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = pages_list

    # obtain the response early and handle the cookies
    visitor_cookie_handler(request)

    response = render(request, 'rango/index.html', context=context_dict)
    # Return a rendered response to send to the client
    return response


def about(request):
    visitor_cookie_handler(request)

    context_dict = {}
    context_dict['visits'] = request.session['visits']

    return render(request, 'rango/about.html', context=context_dict)


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


@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            # the form contained errors, print them to the terminal
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect(reverse('rango:index'))

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


def register(request):
    # boolean value to check if the registration was successful
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # save the user_form data
            user = user_form.save()

            # hash the password
            user.set_password(user.password)
            user.save()

            # deal with the UserProfile, we don't save the model because
            # we have some attributes to set
            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # save the UserProfile instance
            profile.save()

            # the registration was successful
            registered = True
        else:
            # invalid form or forms
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict = {'user_form': user_form,
                    'profile_form': profile_form,
                    'registered': registered}
    return render(request, 'rango/register.html', context=context_dict)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # check if the user/password combination is valid
        user = authenticate(username=username, password=password)

        # if None there was no user with matching credentials
        if user:
            # check if the account is active
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # the account is inactive
                return HttpResponse('Your Rango account is disabled.')
        else:
            # the login credentials don't match any user
            print(f'Invalid login details: {username}, {password}')
            return HttpResponse('Invalid login details supplied.')
    else:
        return render(request, 'rango/login.html')


@login_required
def restricted(request):

    return render(request, 'rango/restricted.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))


# !HELPER FUNCTIONS

def visitor_cookie_handler(request):
    # get the number of visits to the site with the visits cookie
    # if the cookie doesn't exist then give a default value of 1
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(
        request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(
        last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    # check if it has been more than a day since the last visit
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # update the last visit cookie
        request.session['last_visit'] = str(datetime.now())
    else:
        # set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # udpate/set the visits cookie
    request.session['visits'] = visits


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val

    return val
