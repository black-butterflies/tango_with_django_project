from django.contrib import admin
from rango.models import Category, Page
from rango.models import CategoryAdmin, PageAdmin


admin.site.register(Page, PageAdmin)
admin.site.register(Category, CategoryAdmin)
