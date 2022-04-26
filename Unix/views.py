from asyncio.windows_events import NULL
from calendar import day_abbr
from cgi import test
import cmd
from http.client import HTTP_PORT
from json import load
from optparse import Values
from platform import machine
import re
from turtle import update
from django.http import HttpResponse
from django.shortcuts import redirect, render

#Libraries to authenticate the user and then login and logout and show error if authentication data is incorrect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User

#Library to run commands on a machine
import random
import os
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
        username = request.POST.get('username')
        password = request.POST.get('password')
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
            form.save()
            return redirect('login')
        else:
            errors = form.errors
            messages.error(request, errors)
            return redirect('signup')
    else:
        form = createUser()
        values = {'form': form}
        return render(request, 'signup.html', values)

def serverData(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            user = request.user
            form = serverConfig(request.POST)
            if form.is_valid():
                hostname = form.cleaned_data.get('hostname')
                IPAddr = form.cleaned_data.get('IPAddr')
                passwd = form.cleaned_data.get('passwd')
                sshData.objects.update_or_create(user=user, defaults={'hostname':hostname, 'IPAddr': IPAddr, 'passwd':passwd})
                return redirect('/')
            else:
                messages.error(request, form.errors)
                return redirect('serverData')
        else:
            form = serverConfig()
            user = request.user
            ssh = sshData.objects.filter(user=user)
        
            if ssh:
                ssh = sshData.objects.get(user=user)
                values = {"form": form, "hostname": simplejson.dumps(ssh.hostname), "IP": simplejson.dumps(ssh.IPAddr), "passwd" : simplejson.dumps(ssh.passwd)}
                return render(request, "serverdata.html", values)
            else:
                values = {"form": form}
                return render(request, "serverdata.html", values)

def logoutPage(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')
    else:
        return HttpResponse('Please log in to continue')

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
    if request.user.is_authenticated:
        name_check = []
        if request.method=='POST':
            user = request.user
            if request.POST:
                back_filename = str(request.POST.get('formGroupExampleInput2'))
            else:
                back_filename = '*'
            filename = sshConnect.filename()
            while filename in name_check:
                filename = sshConnect.filename()
            
            #Command for backing up the file entered by the user
            command = 'tar -jcvf' +' ' +filename +' ' +back_filename

            #Executing the command on the server
            if result==False:
                return redirect('error')
            else:
                result = sshConnect.connect(command, user)
                
                return redirect('backupArchive')
        else:
            user = request.user 

            #Command to get the list of files
            command = 'ls --file-type'
            #List to store the output 
            test_lst = []
            test2_lst = []
            output_lst_name = []
            output_lst_name2 = []

            #Actual code
            result = sshConnect.connect(command, user)
            if result == False:
                return redirect('error')
            else:
                if len(result)!=0:
                    for val in result:
                        temp1 = val.split(",")
                        for data in temp1:
                            test_lst.append(data.split(":"))
                for data in test_lst:
                    for val in data:
                        test2_lst.append(val)

                for val in test2_lst[0::2]:
                    output_lst_name.append(val)
                for val in test2_lst[1::2]:
                    output_lst_name2.append(val)

                name_check = output_lst_name
                main_result = dict(zip(output_lst_name, output_lst_name2))
                values = {'res': main_result}
                return render(request, 'backuparchive.html', values)


    else:
        return HttpResponse("Please Log in to continue")


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
        if result == False:
            return redirect('error')
        else:
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
        if result == False:
            return redirect('error')
        else:
            if len(result)!=0:
                for val in result:
                    login.append(val.split())

            result = sshConnect.connect(badLogin_command, user)
            if len(result)!=0:
                for val in result:
                    badLogin.append(val.split(": "))

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
        if result == False:
            return redirect('error')
        else:
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
        if result == False:
            return redirect('error')
        else:
            for val in result:
                sample_lst = val.split(":")
            mem_util_lst = sample_lst[1].split()

            mem_lst_pie.append(int(mem_util_lst[0]) - int(mem_util_lst[2]))
            mem_lst_pie.append(mem_util_lst[2])

            mem_lst_bar.append(mem_util_lst[1])
            mem_lst_bar.append(mem_util_lst[3])
            mem_lst_bar.append(mem_util_lst[4])


        result = sshConnect.connect(cpu_util, user)
        if result == False:
            return redirect('error')
        else:
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

def runCommand(request):
    if request.user.is_authenticated:
        user = request.user
        ssh_login = sshData.objects.get(user=user)
        hostname = ssh_login.hostname
        passwd = ssh_login.passwd
        ip = ssh_login.IPAddr
        command = "ssh " +hostname +"@" +ip
        os.system(('start cmd /k "{0}"').format(command))
        return render(request, 'runcommand.html')
    else:
        return HttpResponse(request, "Please log in to continue.")

def error(request):
    #Function to return the error page when the server is offline or some other exceptions occur
    return render(request, 'error.html')