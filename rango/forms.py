from django import forms
from rango.models import Page, Category


class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=Category.NAME_MAX_LENGTH,
        help_text='Please enter the category name.')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # provide additional information on the form
    class Meta:
        model = Category
        fields = ('name', )


class PageForm(forms.ModelForm):
    title = forms.CharField(
        max_length=Page.TITLE_MAX_LENGTH,
        help_text='Please enter the title of the page.')
    url = forms.URLField(
        max_length=Page.URL_MAX_LENGTH,
        help_text='Please enter the URL of the page.')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page
        # what fields are we including in the form?
        # we don't want to include the category field so we exclude it.
        exclude = ('category', )
        # we could also do
        # fields = ('title', 'url', 'views')

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # if url is not empty and doesn't start with 'http://'
        if url and not url.startswith(('http://', 'https://')):
            url = f'http://{url}'
            cleaned_data['url'] = url

        # always return the dictionary, otherwise the changes won't be applied
        return cleaned_data
