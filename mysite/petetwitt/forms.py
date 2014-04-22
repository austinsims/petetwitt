from django import forms
from django.core.exceptions import ValidationError
from HTMLParser import HTMLParser
from petetwitt.models import *
from registration.forms import RegistrationForm
from tinymce.widgets import TinyMCE

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
        in_reply_to = None
        if 'body' in kwargs:
            body = kwargs.pop('body')
        if 'in_reply_to' in kwargs:
            in_reply_to = kwargs.pop('in_reply_to')
        super(TweetForm, self).__init__(*args, **kwargs)
        self.fields['body'].initial = body
        self.fields['in_reply_to'].initial = in_reply_to

    body = forms.CharField(label='', widget=TinyMCE(attrs={"cols":60, "rows": 5,}, mce_attrs={"theme":"advanced", "theme_advanced_buttons1":"bold,italic,underline,forecolor,fontsizeselect,fontselect"}))
    in_reply_to = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=Tweet.objects.all(), required=False)
    
    #TODO picture upload input
    
    def clean_body(self):
        form_data = self.cleaned_data
        if len(strip_tags(form_data['body'])) > 140:
            raise forms.ValidationError("Tweet too long.")
        return form_data['body']

    # def clean_in_reply_to(self):
    #     return self.cleaned_data['in_reply_to']
            
class CustomRegistrationForm(RegistrationForm):
    first_name = forms.CharField(widget=forms.TextInput(), label="First name")
    last_name = forms.CharField(widget=forms.TextInput(), label="Last name")

def user_created(sender, user, request, **kwargs):
    form = CustomRegistrationForm(request.POST)
    user.first_name = form.data['first_name']
    user.last_name = form.data['last_name']
    user.save()

from registration.signals import user_registered
user_registered.connect(user_created)
