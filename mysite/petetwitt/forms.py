from django import forms
from django.core.exceptions import ValidationError
from HTMLParser import HTMLParser
from petetwitt.models import *

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class TweetForm(forms.Form):

    def __init__(self, *args, **kwargs):
        body = ''
        if 'body' in kwargs:
            body = kwargs.pop('body')
        super(TweetForm, self).__init__(*args, **kwargs)
        self.fields['body'].initial = body

    body = forms.CharField(widget=forms.Textarea)
    
    #TODO picture upload input
    
    def clean_body(self):
        form_data = self.cleaned_data
        if len(strip_tags(form_data['body'])) > 140:
            raise forms.ValidationError("Tweet too long.")
        return form_data['body']
            
