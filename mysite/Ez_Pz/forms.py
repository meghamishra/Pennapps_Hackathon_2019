from django import forms

class SearchForm(forms.Form):
    keyword = forms.CharField( label='keyword', max_length=100)