from asyncio.windows_events import NULL
from calendar import day_abbr
from json import load
from optparse import Values
from platform import machine
import re
from django.http import HttpResponse
from django.shortcuts import redirect, render

#Libraries to authenticate the user and then login and logout and show error if authentication data is incorrect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

#Library to run commands on a machine
from subprocess import check_output
import paramiko
from paramiko import BadHostKeyException
from paramiko import AuthenticationException
from paramiko import SSHException

from .models import sshData
from .forms import createUser, serverConfig
from . import sshConnect, models

import json as simplejson

# Create your views here.
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('index')

    elif request.method=='POST':
        username = request.POST.get('hostname')
        password = request.POST.get('passwd')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Username or Password is incorrect!')
            return redirect('login')
    else:
        return render(request, 'login.html',)

def signupPage(request):
    if request.method=='POST':
        form = createUser(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data('username')
            password = form.cleaned_data('password1')
            auth = authenticate(username=username, password=password)
            login(request, auth)
            return redirect('index')
        else:
            messages.error(request, "There was a problem creating account.")
            return redirect('signup')
    else:
        form = createUser()
        values = {'form': form}
        return render(request, 'signup.html', values)

def serverData(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            """ user = request.user
            data = request.POST
            if data:
                hostname = data.getCleanedData("")
                ip = data.getCleanedData("")
                password = data.getCleanedData("") """
        else:
            form = serverConfig()
            user = request.user
            ssh = sshData.objects.get(user=user)
            values = {"form": form, "hostname": simplejson.dumps(ssh.hostname), "IP": simplejson.dumps(ssh.IPAddr), "passwd" : simplejson.dumps(ssh.passwd)}
            return render(request, "serverdata.html", values)

def index(request):
    if request.user.is_authenticated:
        user = request.user
        values = {"user": user}
        return render(request, 'index.html', values)
    elif request.method=="post":
        if request.user.is_authenticated:
            command = str(request.POST)
            result = sshConnect.connect(command)
            values = {"output": result}
            return(request, 'index.html', values)
    else:
        return HttpResponse("<h1>Please log in to continue.<h1>")

def backup(request):
    logout(request)
    return redirect('login')
    #return render(request, "backuparchive.html", )

def process(request):
    if request.user.is_authenticated:
        user = request.user

        process_cmd = "top -b | head -n 12"

        #List to store the data from the top command
        process_list = []
        upperPart = []
        usersLoad = []
        lst1 = []
        users = ""
        loadAverage = ""
        tasks_out = ""
        cpu_out = ""
        ram_out = ""
        swap_out = ""

        #Executing command to get the result
        result = sshConnect.connect(process_cmd, user)
        if len(result)!=0:
            for val in result:
                upperPart.append(val.split("\n"))
            
        #For retrieving the top 5 running processes
        for val in result[7::1]:
            process_list.append(val.split())

        #For retireving the statistics
        for val in upperPart[0]:
            usersLoad.append(val.split(","))

        for val in usersLoad[0]:
            lst1.append(val)    #We can use the upper part by emptying itd

        users = lst1[1]
        loadAverage = lst1[2] +"," + lst1[3] +"," + lst1[4]
        tasks_out = result[1]
        cpu_out = result[2]
        ram_out = result[3]
        swap_out = result[4]
        
        #Creating a dictionary to pass list values to template
        values = {"users": users, "load": loadAverage, "tasks": tasks_out, "cpu": cpu_out, "ram": ram_out, 'swap': swap_out , "processData": process_list, "fullData": upperPart}

        return render(request, 'monitorprocess.html', values)
    else:
        return HttpResponse("<h1>Please log in to continue.<h1>")

def users(request):
    if request.user.is_authenticated:
        user = request.user
        #To get the data of the logged in users

        #Commands for login and failed login data
        login_command = 'who'
        badLogin_command = 'cat /var/log/auth.log | grep "Failed password"'

        #Lists to store information retrieved from commands
        lst1 = []   #list 1 stores the message part for failed login
        lst2 = []   #list 2 stores the actual data part for failed login
        login = []  #intermediate list to capture and divide data
        badLogin = []
        values = {}
        badLogin_dict = {}

        #Executing both commands and storing data in respective lists
        result = sshConnect.connect(login_command, user)
        if len(result)!=0:
            for val in result:
                login.append(val.split())

        result = sshConnect.connect(badLogin_command, user)
        if len(result)!=0:
            for val in result:
                badLogin.append(val.split(": "))

        """ for val in badLogin[0::2]:
            lst2.append(val.strip(" "))
        
        lst1.clear()
        for val in badLogin[1::2]:
            lst1.append(val) """

        #badLogin_dict = dict(zip(lst2, lst1))

        #Passing the list data to dictionary
        values = {"login": login, "badLogin": badLogin}
        return render(request, 'users.html', values)

    else:
        return HttpResponse("<h1>Please log in to continue.<h1>")

def diskSpace(request):
    if request.user.is_authenticated:
        user = request.user

        #Commands for the three parts of the interfaces
        command_disk = "df -h | sed '1d'"
        command_devsda = "df -h | grep 'dev/sda'"
        command_devsdb = "df -h | grep 'dev/sdb'"

        #List to store the data that is passed to the three interfaces
        lst1 = []
        disk_data = []
        devsda_data = []
        devsdb_data = []

        #Three commands are executed and data is store in the respective list 
        result = sshConnect.connect(command_disk, user)
        if len(result)!=0:
            for val in result:
                lst1.append(val.split("\n"))

        for data in lst1:
            for val in data:
                disk_data.append(val.split())

        lst1.clear()
        result = sshConnect.connect(command_devsda, user)
        if len(result)!=0:
            for val in result:
                lst1.append(val.split("\n"))
        
        for data in lst1:
            for val in data:
                devsda_data.append(val.split())

        lst1.clear()
        result = sshConnect.connect(command_devsdb, user)
        if len(result)!=0:
            for val in result:
                lst1.append(val.split("\n"))
        
        for data in lst1:
            for val in data:
                devsdb_data.append(val.split())

        devsda_data = devsda_data + devsdb_data

        #Data is passed as dictionary to the template
        values = {"diskData": disk_data, "devsdaData": devsda_data}
        return render(request, 'diskspace.html', values)
    else:
        return HttpResponse("<h1>Please log in to continue.<h1>")

def graphicalAnalysis(request):
    if request.user.is_authenticated:
        user = request.user

        #Command for retrieving different datas
        mem_util = "free --mega | grep 'Mem'"
        cpu_util = "mpstat | grep 'all'"

        #List to store the data output
        sample_lst = []
        mem_util_lst = []
        mem_lst_pie = [] #list for only defining used and free memory
        mem_lst_bar = []    #list for defining detailed used memory
        cpu_util_lst = []
        cpu_lst_pie = []
        cpu_lst_bar = []

        #Executing the commands
        result = sshConnect.connect(mem_util, user)
        for val in result:
            sample_lst = val.split(":")
        mem_util_lst = sample_lst[1].split()

        mem_lst_pie.append(int(mem_util_lst[0]) - int(mem_util_lst[2]))
        mem_lst_pie.append(mem_util_lst[2])

        mem_lst_bar.append(mem_util_lst[1])
        mem_lst_bar.append(mem_util_lst[3])
        mem_lst_bar.append(mem_util_lst[4])


        result = sshConnect.connect(cpu_util, user)
        for val in result:
            cpu_util_lst = val.split()
        for i in range (0,3):
            cpu_util_lst.pop(0)

        cpu_lst_pie.append(100-float(cpu_util_lst[9]))
        cpu_lst_pie.append(cpu_util_lst[9])

        cpu_lst_bar.append(cpu_util_lst[0])
        cpu_lst_bar.append(cpu_util_lst[2])
        cpu_lst_bar.append(cpu_util_lst[3])

        #Assigning the values to the variables
        values = {"memory_pie": simplejson.dumps(mem_lst_pie), 'memory_bar': simplejson.dumps(mem_lst_bar), 'cpu_pie': simplejson.dumps(cpu_lst_pie), 'cpu_bar': simplejson.dumps(cpu_lst_bar)}

        return render(request, 'graphicalanalysis.html', values)
    else:
        return HttpResponse("<h1>Please log in to continue.<h1>")   

def cmdOutput(request):
    return render(request, 'cmdoutput.html', )