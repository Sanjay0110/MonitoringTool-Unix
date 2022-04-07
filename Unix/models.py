from ipaddress import ip_address
from tkinter import CASCADE
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class sshData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=100, null=True, blank=True)
    passwd = models.CharField(max_length=100, null=True, blank=True)
    IPAddr = models.GenericIPAddressField(protocol='both', null=True, blank=True)

    def __str__(self):
         return "{0} : {1}".format(self.hostname, self.IPAddr)

