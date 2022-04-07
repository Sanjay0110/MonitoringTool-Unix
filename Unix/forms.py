from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

from Unix.models import sshData

class createUser(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

class serverConfig(forms.ModelForm):

    class Meta:
        model = sshData
        fields = ('hostname', "passwd", "IPAddr")