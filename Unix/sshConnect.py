from .models import sshData
from paramiko import *
import paramiko

import random

def connect(command, user):
    values = []
    ssh_login = sshData.objects.get(user=user)
    username = ssh_login.hostname
    password = ssh_login.passwd
    ip = ssh_login.IPAddr
    ssh = paramiko.client.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username= username, password= password)
        cmd = command
        stdin,stdout,stderr = ssh.exec_command(cmd)
        output = stdout.readlines()
        error = stderr.readlines()
        ssh.close()
        return output
    except Exception as exc: #(BadHostKeyException, AuthenticationException, SSHException)
        return False

""" def getFile(filename, user):
    values = []
    ssh_login = sshData.objects.get(user=user)
    username = ssh_login.hostname
    password = ssh_login.passwd
    ip = ssh_login.IPAddr
    ssh = paramiko.client.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username= username, password= password)
        ftp_client = ssh.open_sftp()
        remoteLocation = "/home/" +username +"/" +filename
        print(remoteLocation)
        ftp_client.get(filename, filename)
        ftp_client.close()
    except(BadHostKeyException, AuthenticationException, SSHException) as exc:
        return exc """


def filename():
    name = 'backive'
    number = random.randint(1,10000)

    name = name+str(number)+'.tar.bz2'
    return name